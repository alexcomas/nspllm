// Central asset configuration for PhaserReplay
// NOTE: Paths assume you will copy or symlink needed assets from
// environment/frontend_server/static_dirs/assets into the SPA public/ directory.
// For now we reference expected public/ paths (Vite serves /public at root).

export interface PersonaAssetConfig {
  frame?: string // future atlas frame reference
  emoji?: string // pronunciatio fallback
  image?: string // direct image path
}

export const personaAssets: Record<string, PersonaAssetConfig> = {
  'Isabella Rodriguez': { image: '/assets/characters/Isabella_Rodriguez.png', emoji: '🎨' },
  'Klaus Mueller': { image: '/assets/characters/Klaus_Mueller.png', emoji: '🧪' },
  'Maria Lopez': { image: '/assets/characters/Maria_Lopez.png', emoji: '📚' },
  'John Lin': { image: '/assets/characters/John_Lin.png', emoji: '🛠️' },
  'Hailey Johnson': { image: '/assets/characters/Hailey_Johnson.png', emoji: '🎵' },
  'Arthur Burton': { image: '/assets/characters/Arthur_Burton.png', emoji: '🧠' },
  'Abigail Chen': { image: '/assets/characters/Abigail_Chen.png', emoji: '🔬' },
  'Carlos Gomez': { image: '/assets/characters/Carlos_Gomez.png', emoji: '💬' },
  'Jane Moreno': { image: '/assets/characters/Jane_Moreno.png', emoji: '📰' },
  'Tom Moreno': { image: '/assets/characters/Tom_Moreno.png', emoji: '💼' },
  'Sam Moore': { image: '/assets/characters/Sam_Moore.png', emoji: '⚽' },
  'Latoya Williams': { image: '/assets/characters/Latoya_Williams.png', emoji: '🛍️' },
  'Ayesha Khan': { image: '/assets/characters/Ayesha_Khan.png', emoji: '🧵' },
  'Rajiv Patel': { image: '/assets/characters/Rajiv_Patel.png', emoji: '💻' },
  'Wolfgang Schulz': { image: '/assets/characters/Wolfgang_Schulz.png', emoji: '🎻' },
  'Yuriko Yamamoto': { image: '/assets/characters/Yuriko_Yamamoto.png', emoji: '🌸' },
  'Mei Lin': { image: '/assets/characters/Mei_Lin.png', emoji: '🧮' },
  'Ryan Park': { image: '/assets/characters/Ryan_Park.png', emoji: '🏃' },
  'Jennifer Moore': { image: '/assets/characters/Jennifer_Moore.png', emoji: '📖' },
  'Adam Smith': { image: '/assets/characters/Adam_Smith.png', emoji: '📊' },
  'Carmen Ortiz': { image: '/assets/characters/Carmen_Ortiz.png', emoji: '🍳' },
  'Eddy Lin': { image: '/assets/characters/Eddy_Lin.png', emoji: '🧩' },
  'Giorgio Rossi': { image: '/assets/characters/Giorgio_Rossi.png', emoji: '🍷' },
  'Francisco Lopez': { image: '/assets/characters/Francisco_Lopez.png', emoji: '🚗' },
  'Tamara Taylor': { image: '/assets/characters/Tamara_Taylor.png', emoji: '🎬' },
}

export interface TilesetConfig {
  key: string
  path: string
  tileWidth?: number
  tileHeight?: number
  margin?: number
  spacing?: number
}

export const tilemapConfig = {
  mapJson: '/assets/the_ville/visuals/the_ville_jan7.json',
  // All tilesets from the Tiled map JSON with proper dimensions - ensure these exist in public folder.
  tilesets: [
    { key: 'CuteRPG_Field_B', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Field_B.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Field_C', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Field_C.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Harbor_C', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Harbor_C.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'Room_Builder_32x32', path: '/assets/the_ville/visuals/map_assets/v1/Room_Builder_32x32.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Village_B', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Village_B.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Forest_B', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Forest_B.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Desert_C', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Desert_C.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Mountains_B', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Mountains_B.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Desert_B', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Desert_B.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'CuteRPG_Forest_C', path: '/assets/the_ville/visuals/map_assets/cute_rpg_word_VXAce/tilesets/CuteRPG_Forest_C.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'interiors_pt1', path: '/assets/the_ville/visuals/map_assets/v1/interiors_pt1.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'interiors_pt2', path: '/assets/the_ville/visuals/map_assets/v1/interiors_pt2.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'interiors_pt3', path: '/assets/the_ville/visuals/map_assets/v1/interiors_pt3.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'interiors_pt4', path: '/assets/the_ville/visuals/map_assets/v1/interiors_pt4.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'interiors_pt5', path: '/assets/the_ville/visuals/map_assets/v1/interiors_pt5.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'blocks', path: '/assets/the_ville/visuals/map_assets/blocks/blocks_1.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'blocks_2', path: '/assets/the_ville/visuals/map_assets/blocks/blocks_2.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
    { key: 'blocks_3', path: '/assets/the_ville/visuals/map_assets/blocks/blocks_3.png', tileWidth: 32, tileHeight: 32, margin: 0, spacing: 0 },
  ] as TilesetConfig[],
  // Layers we will attempt to render (must match names inside JSON)
  layers: [
    'Bottom Ground',
    'Exterior Ground',
    'Exterior Decoration L1',
    'Exterior Decoration L2',
    'Interior Ground',
    'Wall',
    'Interior Furniture L1',
    'Interior Furniture L2 ',
    'Foreground L1',
    'Foreground L2'
  ],
}

export function extractEmojiFromAction(action: string | undefined, fallback?: string) {
  if (!action) return fallback || ''
  const m = action.match(/^(\p{Emoji_Presentation}|\p{Emoji}\uFE0F)\s/iu)
  return m ? m[1] : (fallback || '')
}
