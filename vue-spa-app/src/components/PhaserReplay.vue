<template>
  <div class="phaser-replay" ref="container">
    <div v-if="!replay" class="empty">No replay loaded</div>
    <div class="zoom-controls">
      <button @click="zoomOut" title="Zoom Out">-</button>
      <button @click="zoomIn" title="Zoom In">+</button>
    </div>
    <div class="layer-controls">
      <label v-for="layer in allLayerOptions" :key="layer" class="layer-checkbox">
        <input type="checkbox" :value="layer" v-model="selectedLayers" />
        {{ layer }}
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
// All possible layers (from config)
const allLayerOptions = tilemapConfig.layers
// User-selected layers to render
const selectedLayers = ref([...tilemapConfig.layers])

// Watch for changes to selectedLayers and re-init Phaser game
watch(selectedLayers, () => {
  if (game) {
    game.destroy(true)
    game = null
  }
  // Clear sprite and label maps to avoid referencing destroyed objects
  for (const k in spriteMap) { spriteMap[k].destroy?.(); delete spriteMap[k]; }
  for (const k in labelMap) { labelMap[k].destroy?.(); delete labelMap[k]; }
  // Wait for DOM cleanup
  setTimeout(() => {
    initGame()
    // Restore zoom after re-init
    setTimeout(() => {
      if (game && game.scene.keys['ReplayScene']) {
        game.scene.keys['ReplayScene'].cameras.main.setZoom(zoom.value)
      }
    }, 300)
  }, 0)
}, { deep: true })
// Camera zoom state
import { ref as vueRef } from 'vue'
const zoom = vueRef(1)
const minZoom = 0.5
const maxZoom = 2.5
const zoomStep = 0.2

function zoomIn() {
  zoom.value = Math.min(maxZoom, zoom.value + zoomStep)
  if (game && game.scene.keys['ReplayScene']) {
    game.scene.keys['ReplayScene'].cameras.main.setZoom(zoom.value)
  }
}
function zoomOut() {
  zoom.value = Math.max(minZoom, zoom.value - zoomStep)
  if (game && game.scene.keys['ReplayScene']) {
    game.scene.keys['ReplayScene'].cameras.main.setZoom(zoom.value)
  }
}
import { onMounted, onUnmounted, ref, watch, computed } from 'vue'
import Phaser from 'phaser'
import type { Replay, ReplayFrame } from '@/types'
import { tilemapConfig, personaAssets, extractEmojiFromAction } from '@/assets/replayAssets'

interface Props {
  replay: Replay | null
  frameIndex: number
  focusedAgentId?: string | null // agent to focus camera on
}

const props = defineProps<Props>()
const container = ref<HTMLDivElement | null>(null)
let game: Phaser.Game | null = null
let cameraFollowActive = true // disables after drag, re-enabled by parent

// Internal caches
const spriteMap: Record<string, Phaser.GameObjects.Sprite> = {}
const labelMap: Record<string, Phaser.GameObjects.Text> = {}

// Basic frame accessor
const frame = computed<ReplayFrame | null>(() => props.replay ? props.replay.frames[props.frameIndex] : null)

// Placeholder world bounds (will compute from frames) 
function computeBounds() {
  if (!props.replay) return { minX:0, maxX:100, minY:0, maxY:100 }
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  for (const f of props.replay.frames) {
    for (const a of f.agents) {
      if (a.location.x < minX) minX = a.location.x
      if (a.location.x > maxX) maxX = a.location.x
      if (a.location.y < minY) minY = a.location.y
      if (a.location.y > maxY) maxY = a.location.y
    }
  }
  if (minX === Infinity) return { minX:0, maxX:100, minY:0, maxY:100 }
  if (minX === maxX) maxX += 1
  if (minY === maxY) maxY += 1
  return { minX, maxX, minY, maxY }
}

const bounds = computeBounds()


// Scaling helpers - converts tile coordinates to pixel coordinates
function tileToPixel(tileX: number, tileY: number): { x: number, y: number } {
  const TILE_SIZE = 32; // Standard tile size from Tiled
  return {
    x: tileX * TILE_SIZE + TILE_SIZE / 2, // Center of tile
    y: tileY * TILE_SIZE + TILE_SIZE / 2  // Center of tile
  };
}

// Camera follow state (module-level, so we can expose a method)
// Expose a method for parent to re-enable camera follow
function focusAgent() {
  cameraFollowActive = true
}
defineExpose({ focusAgent })

class ReplayScene extends Phaser.Scene {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  private map?: Phaser.Tilemaps.Tilemap
  constructor() { super('ReplayScene') }
  preload() {
    // Tilesets & map
    this.load.tilemapTiledJSON('world_map_json', tilemapConfig.mapJson)
    for (const ts of tilemapConfig.tilesets) {
      this.load.image(ts.key, ts.path)
    }
    // Persona images
    for (const [name, cfg] of Object.entries(personaAssets)) {
      if (cfg.image) {
        const key = personaKey(name)
        if (!this.textures.exists(key)) this.load.image(key, cfg.image)
      }
    }
    // Fallback circle
    // const g = this.add.graphics()
    // g.fillStyle(0x42b883, 1)
    // g.fillCircle(16,16,16)
    // g.generateTexture('agent_circle', 32,32)
    // g.destroy()
  }
  create() {
    this.cameras.main.setBackgroundColor('#f0f0f0')
    this.buildMap()
    this.time.addEvent({ delay: 200, loop: true, callback: () => this.refreshFrame() })

    // Enable camera panning and dragging
    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      if (pointer.rightButtonDown() || pointer.middleButtonDown() || pointer.leftButtonDown()) {
        this.input.setDefaultCursor('grabbing')
        this._dragStartX = pointer.x
        this._dragStartY = pointer.y
        this._camStartX = this.cameras.main.scrollX
        this._camStartY = this.cameras.main.scrollY
        this._dragging = true
      }
    })
    this.input.on('pointerup', () => {
      this.input.setDefaultCursor('default')
      this._dragging = false
      // Disable camera follow after drag
      cameraFollowActive = false
    })
    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      if (this._dragging) {
        const dx = pointer.x - this._dragStartX
        const dy = pointer.y - this._dragStartY
        this.cameras.main.scrollX = this._camStartX - dx
        this.cameras.main.scrollY = this._camStartY - dy
      }
    })
    // Prevent context menu on right drag
    this.game.canvas.oncontextmenu = (e) => { e.preventDefault() }
  }
  // Camera drag state
  private _dragging = false
  private _dragStartX = 0
  private _dragStartY = 0
  private _camStartX = 0
  private _camStartY = 0
  buildMap() {
    console.log('Building map with tilemap JSON - Python style');
    
    // Create the tilemap
    const map = this.make.tilemap({ key: 'world_map_json' });
    console.log('Created tilemap:', map);
    
    // Add tilesets using the exact names from the JSON, following Python implementation
    const collisions = map.addTilesetImage("blocks", "blocks");
    const blocks_2 = map.addTilesetImage("blocks_2", "blocks_2");
    const blocks_3 = map.addTilesetImage("blocks_3", "blocks_3");
    const walls = map.addTilesetImage("Room_Builder_32x32", "Room_Builder_32x32");
    const interiors_pt1 = map.addTilesetImage("interiors_pt1", "interiors_pt1");
    const interiors_pt2 = map.addTilesetImage("interiors_pt2", "interiors_pt2");
    const interiors_pt3 = map.addTilesetImage("interiors_pt3", "interiors_pt3");
    const interiors_pt4 = map.addTilesetImage("interiors_pt4", "interiors_pt4");
    const interiors_pt5 = map.addTilesetImage("interiors_pt5", "interiors_pt5");
    const CuteRPG_Field_B = map.addTilesetImage("CuteRPG_Field_B", "CuteRPG_Field_B");
    const CuteRPG_Field_C = map.addTilesetImage("CuteRPG_Field_C", "CuteRPG_Field_C");
    const CuteRPG_Harbor_C = map.addTilesetImage("CuteRPG_Harbor_C", "CuteRPG_Harbor_C");
    const CuteRPG_Village_B = map.addTilesetImage("CuteRPG_Village_B", "CuteRPG_Village_B");
    const CuteRPG_Forest_B = map.addTilesetImage("CuteRPG_Forest_B", "CuteRPG_Forest_B");
    const CuteRPG_Desert_C = map.addTilesetImage("CuteRPG_Desert_C", "CuteRPG_Desert_C");
    const CuteRPG_Mountains_B = map.addTilesetImage("CuteRPG_Mountains_B", "CuteRPG_Mountains_B");
    const CuteRPG_Desert_B = map.addTilesetImage("CuteRPG_Desert_B", "CuteRPG_Desert_B");
    const CuteRPG_Forest_C = map.addTilesetImage("CuteRPG_Forest_C", "CuteRPG_Forest_C");
    
    console.log('Added all tilesets');
    
    // Create tileset groups like in Python implementation
    const tileset_group_1 = [
      CuteRPG_Field_B, CuteRPG_Field_C, CuteRPG_Harbor_C, CuteRPG_Village_B, 
      CuteRPG_Forest_B, CuteRPG_Desert_C, CuteRPG_Mountains_B, CuteRPG_Desert_B, CuteRPG_Forest_C,
      interiors_pt1, interiors_pt2, interiors_pt3, interiors_pt4, interiors_pt5, walls,
      collisions, blocks_2, blocks_3
    ].filter(t => t !== null); // Filter out any null tilesets
    
    // Create layers exactly like the Python implementation, but only if selected by user
    try {
      console.log('Selected layers:', selectedLayers.value);
      
      if (selectedLayers.value.includes("Bottom Ground")) {
        console.log('Creating Bottom Ground layer...');
        const bottomGroundLayer = map.createLayer("Bottom Ground", tileset_group_1, 0, 0);
        if (bottomGroundLayer) {
          console.log('✓ Bottom Ground layer created successfully');
          bottomGroundLayer.setDepth(0); // Bottom layer
        } else {
          console.error('✗ Failed to create Bottom Ground layer');
        }
      }
      
      if (selectedLayers.value.includes("Exterior Ground")) {
        const exteriorGroundLayer = map.createLayer("Exterior Ground", tileset_group_1, 0, 0);
        if (exteriorGroundLayer) exteriorGroundLayer.setDepth(1);
      }
      
      if (selectedLayers.value.includes("Exterior Decoration L1")) {
        const exteriorDecorationL1Layer = map.createLayer("Exterior Decoration L1", tileset_group_1, 0, 0);
        if (exteriorDecorationL1Layer) exteriorDecorationL1Layer.setDepth(2);
      }
      
      if (selectedLayers.value.includes("Exterior Decoration L2")) {
        const exteriorDecorationL2Layer = map.createLayer("Exterior Decoration L2", tileset_group_1, 0, 0);
        if (exteriorDecorationL2Layer) exteriorDecorationL2Layer.setDepth(3);
      }
      
      if (selectedLayers.value.includes("Interior Ground")) {
        const interiorGroundLayer = map.createLayer("Interior Ground", tileset_group_1, 0, 0);
        if (interiorGroundLayer) interiorGroundLayer.setDepth(4);
      }
      
      if (selectedLayers.value.includes("Wall")) {
        console.log('Creating Wall layer...');
        // Include all tilesets that contain wall tiles based on analysis of the data
        const wallLayer = map.createLayer("Wall", tileset_group_1, 0, 0);
        if (wallLayer) {
          wallLayer.setDepth(10); // Make sure walls render above ground layers
          console.log('✓ Wall layer created with high depth');
        }
      }
      
      if (selectedLayers.value.includes("Interior Furniture L1")) {
        const interiorFurnitureL1Layer = map.createLayer("Interior Furniture L1", tileset_group_1, 0, 0);
        if (interiorFurnitureL1Layer) interiorFurnitureL1Layer.setDepth(5);
      }
      
      if (selectedLayers.value.includes("Interior Furniture L2 ")) {
        const interiorFurnitureL2Layer = map.createLayer("Interior Furniture L2 ", tileset_group_1, 0, 0);
        if (interiorFurnitureL2Layer) interiorFurnitureL2Layer.setDepth(6);
      }
      
      if (selectedLayers.value.includes("Foreground L1")) {
        const foregroundL1Layer = map.createLayer("Foreground L1", tileset_group_1, 0, 0);
        if (foregroundL1Layer) foregroundL1Layer.setDepth(20); // Above everything
      }
      
      if (selectedLayers.value.includes("Foreground L2")) {
        const foregroundL2Layer = map.createLayer("Foreground L2", tileset_group_1, 0, 0);
        if (foregroundL2Layer) foregroundL2Layer.setDepth(21); // Above everything
      }
      
      if (selectedLayers.value.includes("Collisions")) {
        const collisionsLayer = map.createLayer("Collisions", [collisions].filter(t => t !== null), 0, 0);
        if (collisionsLayer) {
          collisionsLayer.setCollisionByProperty({ collide: true });
          collisionsLayer.setDepth(30); // Debug layer on top
        }
      }
      
      console.log('All selected layers created');
      
    } catch (error) {
      console.error('Error creating layers:', error);
    }
    
    this.map = map;
  }
  refreshFrame() {
    if (!frame.value) return
    const scene = this
    const present = new Set<string>()
    // Camera follow: focus on focusedAgentId if set and cameraFollowActive, but only if not dragging
    const focusedId = props.focusedAgentId
    if (focusedId && cameraFollowActive && !this._dragging) {
      const agent = frame.value.agents.find(a => a.id === focusedId)
      if (agent) {
        const { x, y } = tileToPixel(agent.location.x, agent.location.y)
        this.cameras.main.pan(x, y, 200, 'Sine.easeInOut', false)
      }
    }
    for (const agent of frame.value.agents) {
      present.add(agent.id)
      let sprite = spriteMap[agent.id]
      let label = labelMap[agent.id]
      const personaCfg = personaAssets[agent.name]
      const key = personaCfg?.image ? personaKey(agent.name) : 'agent_circle'
      // --- SPRITESHEET ANIMATION LOGIC ---
      // 4 rows (front, left, right, back), 3 cols (walk1, idle, walk2)
      // Determine direction and animation frame
      let prev = (agent as any).prev_location || agent.location
      let dx = agent.location.x - prev.x
      let dy = agent.location.y - prev.y
      let dir = 0 // 0:down, 1:left, 2:right, 3:up
      if (Math.abs(dx) > Math.abs(dy)) {
        dir = dx > 0 ? 2 : 1
      } else if (Math.abs(dy) > 0.1) {
        dir = dy > 0 ? 0 : 3
      }
      // Animation: alternate between walk1/walk2 if moving, else idle
      let moving = Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1
      let animCol = 1 // idle
      if (moving) {
        // Use frameIndex to alternate
        animCol = (Math.floor((frame.value?.step || 0) / 8) % 2 === 0) ? 0 : 2
      }
      // Frame size (assume 32x32)
      const frameW = 32, frameH = 32
      const frameX = animCol * frameW
      const frameY = dir * frameH
      if (!sprite) {
        if (personaCfg?.image && !this.textures.exists(key)) {
          // (If late) attempt lazy load; in practice should already be loaded
          this.load.image(key, personaCfg.image)
          this.load.once(Phaser.Loader.Events.COMPLETE, () => this.createOrUpdateAgent(agent, key))
          this.load.start()
          continue
        }
        sprite = this.add.sprite(0,0,key)
        sprite.setData('id', agent.id)
        sprite.setOrigin(0.5, 0.85)
        spriteMap[agent.id] = sprite
        // Add label (emoji or initials)
        const bubble = extractEmojiFromAction(agent.current_action, personaCfg?.emoji)
        const labelText = bubble ? `${bubble}` : initials(agent.name)
        label = this.add.text(0,0,labelText, { fontSize:'16px', color:'#fff', fontFamily:'sans-serif', stroke:'#000', strokeThickness:3, backgroundColor:'rgba(0,0,0,0.3)', padding:{left:4,right:4,top:2,bottom:2} }).setOrigin(0.5)
        labelMap[agent.id] = label
      }
      // Set correct frame from spritesheet
      if (sprite && personaCfg?.image) {
        sprite.setTexture(key)
        sprite.setCrop(frameX, frameY, frameW, frameH)
      }
      const { x, y } = tileToPixel(agent.location.x, agent.location.y)
      // Tween movement for smoothness
      if (sprite && (Math.abs(sprite.x - x) > 1 || Math.abs(sprite.y - y) > 1)) {
        this.tweens.add({ targets: sprite, x, y, duration: 180, ease: 'Sine.easeInOut' })
      } else if (sprite) {
        sprite.setPosition(x, y)
      }
      sprite.setDepth(y)
      // Pronunciatio overlay (emoji or text bubble)
      const bubble = extractEmojiFromAction(agent.current_action, personaCfg?.emoji)
      const labelText = bubble ? `${bubble}` : initials(agent.name)
      if (label) {
        label.setText(labelText)
        // Tween label too
        if (Math.abs(label.x - x) > 1 || Math.abs(label.y - (y - 40)) > 1) {
          this.tweens.add({ targets: label, x, y: y - 40, duration: 180, ease: 'Sine.easeInOut' })
        } else {
          label.setPosition(x, y - 40)
        }
        label.setDepth(y + 1000)
      }
    }
    // Remove missing
    for (const id of Object.keys(spriteMap)) {
      if (!present.has(id)) {
        spriteMap[id].destroy(); delete spriteMap[id]
        labelMap[id]?.destroy(); delete labelMap[id]
      }
    }
  }

  createOrUpdateAgent(agent: any, key: string) {
    let sprite = spriteMap[agent.id]
    if (!sprite) {
      sprite = this.add.sprite(0,0,key).setOrigin(0.5,0.85)
      spriteMap[agent.id] = sprite
    } else {
      sprite.setTexture(key)
    }
  }
}

function personaKey(name: string) { return `persona_${name.replace(/\s+/g,'_')}` }

function initials(name: string) {
  return name.split(/\s+/).map(s=>s[0]).join('').slice(0,2).toUpperCase()
}

function initGame() {
  if (!container.value) return
  game = new Phaser.Game({
    type: Phaser.AUTO,
    width: container.value.clientWidth || 800,
    height: 480,
    parent: container.value,
    backgroundColor: '#ffffff',
    scene: [ReplayScene],
    scale: { mode: Phaser.Scale.RESIZE, autoCenter: Phaser.Scale.CENTER_BOTH },
  physics: { default: 'arcade', arcade: { gravity: { x: 0, y: 0 } } }
  })
}


onMounted(() => {
  initGame()
  // Set initial zoom after game is ready
  setTimeout(() => {
    if (game && game.scene.keys['ReplayScene']) {
      game.scene.keys['ReplayScene'].cameras.main.setZoom(zoom.value)
    }
  }, 300)
})

onUnmounted(() => { if (game) { game.destroy(true); game = null } })

// When frame index changes ensure scene picks up new data quickly
watch(() => props.frameIndex, () => {
  // We rely on the scene refresh loop reading frame.value
}, { flush: 'post' })

// Watch for focusedAgentId changes: re-enable camera follow
watch(() => props.focusedAgentId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    cameraFollowActive = true
  }
})

watch(() => props.replay, () => {
  // Future: rebuild bounds & maybe rebuild map layers if map tied to scenario
})
</script>

<style scoped>
.phaser-replay {
  position: relative;
  width: 100%;
  max-width: 800px;
  height: 480px;
  min-height: 480px;
  overflow: hidden;
  border:1px solid #d8dfe6;
  border-radius:8px;
  background:#f5f7fa;
  margin: 0 auto;
  box-sizing: border-box;
}
.empty { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:#777; font-size:0.9rem; }
.layer-controls {
  position: absolute;
  left: 12px;
  top: 12px;
  z-index: 11;
  background: rgba(255,255,255,0.95);
  border-radius: 8px;
  padding: 8px 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 90%;
  overflow-y: auto;
}
.layer-checkbox {
  font-size: 0.95rem;
  user-select: none;
  white-space: nowrap;
}
  .zoom-controls {
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 10;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .zoom-controls button {
    width: 32px;
    height: 32px;
    font-size: 1.5rem;
    background: #fff;
    border: 1px solid #bbb;
    border-radius: 6px;
    cursor: pointer;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    transition: background 0.15s;
  }
  .zoom-controls button:hover {
    background: #f0f0f0;
  }
</style>
