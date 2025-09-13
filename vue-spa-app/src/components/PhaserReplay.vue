<template>
  <div class="phaser-replay" ref="container">
    <div v-if="!replay" class="empty">No replay loaded</div>
    <div class="zoom-controls">
      <button @click="zoomOut" title="Zoom Out">-</button>
      <button @click="zoomIn" title="Zoom In">+</button>
    </div>
  </div>
</template>

<script setup lang="ts">
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


// Scaling helpers
function worldToScreen(x:number, y:number, scene: Phaser.Scene) {
  const pad = 32
  const w = scene.scale.width - pad * 2
  const h = scene.scale.height - pad * 2
  const sx = pad + ( (x - bounds.minX) / (bounds.maxX - bounds.minX) ) * w
  const sy = pad + ( (y - bounds.minY) / (bounds.maxY - bounds.minY) ) * h
  return { x: sx, y: sy }
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
    this.load.json('world_map_json', tilemapConfig.mapJson)
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
    const g = this.add.graphics()
    g.fillStyle(0x42b883, 1)
    g.fillCircle(16,16,16)
    g.generateTexture('agent_circle', 32,32)
    g.destroy()
  }
  create() {
    this.cameras.main.setBackgroundColor('#1e1f22')
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
    // Destroy previous map and layers if they exist
    if (this.map) {
      this.map.layers.forEach((layer: any) => {
        if (layer.tilemapLayer && layer.tilemapLayer.destroy) {
          layer.tilemapLayer.destroy();
        }
      });
      this.map.destroy();
      this.map = undefined;
    }
    try {
      const raw: any = this.cache.json.get('world_map_json')
      if (!raw) throw new Error('Tilemap JSON missing')
      // Create Phaser tilemap from Tiled JSON
      const map = this.make.tilemap({ data: undefined, key: 'world_map_json', tileWidth: 32, tileHeight: 32 })
      // Add tilesets
      const tilesetObjs: Record<string, Phaser.Tilemaps.Tileset> = {}
      for (const ts of tilemapConfig.tilesets) {
        const tileset = map.addTilesetImage(ts.key, ts.key)
        if (tileset) tilesetObjs[ts.key] = tileset
      }
      // Render layers in order
      for (const layerName of tilemapConfig.layers) {
        const layerData = raw.layers.find((l:any) => l.name === layerName && l.type === 'tilelayer')
        if (!layerData) continue
        // Compose tileset array for this layer (Phaser expects all tilesets, even if not used)
        const tilesets = Object.values(tilesetObjs)
        // Create blank layer and populate with data
        const tileLayer = map.createBlankLayer(layerName, tilesets, 0, 0)
        if (tileLayer && Array.isArray(layerData.data)) {
          for (let y = 0; y < layerData.height; y++) {
            for (let x = 0; x < layerData.width; x++) {
              const idx = y * layerData.width + x
              const gid = layerData.data[idx]
              if (gid > 0) tileLayer.putTileAt(gid - 1, x, y)
            }
          }
          tileLayer.setDepth(layerData.id || 0)
        }
      }
      this.map = map
    } catch (e) {
      console.warn('[PhaserReplay] Map build failed', e)
    }
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
        const { x, y } = worldToScreen(agent.location.x, agent.location.y, scene)
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
      let prev = agent.prev_location || agent.location
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
        animCol = (Math.floor(frame.value?.step/8 ?? 0) % 2 === 0) ? 0 : 2
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
      const { x, y } = worldToScreen(agent.location.x, agent.location.y, scene)
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
.phaser-replay { position: relative; width: 100%; min-height: 480px; border:1px solid #d8dfe6; border-radius:8px; background:#f5f7fa; }
.empty { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:#777; font-size:0.9rem; }
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
