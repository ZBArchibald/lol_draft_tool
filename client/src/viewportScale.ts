// Fits the full desktop layout to the window (CSS `zoom` on <html>), scaling UP or
// down, so any landscape screen - a 16:9 monitor, a small window, a phone held
// sideways - shows the same layout filling the screen.
//
// - The design canvas is DESIGN_WIDTH x DESIGN_HEIGHT; zoom = whichever ratio is
//   tighter. Leftover width is filled by the board (no max-width), leftover height
//   sits between the board and the bottom recommendations bar.
// - Touch screens held upright (portrait phones) are the exception: zoom 1 and the
//   responsive narrow layout + rotate-your-phone prompt.
// - Below MIN_ZOOM the page would be unreadable, so it falls back to zoom 1.
// - Media and container queries also measure in window (zoomed) px, so the narrow
//   (phone) layout is switched by a data-layout="narrow" attribute on <html>,
//   decided here from the true layout width; data-layout="compact" marks phones
//   held sideways (see COMPACT_*).
// - Under `zoom`, `vw`/`vh` are NOT compensated and getBoundingClientRect()
//   returns zoomed (visual) coordinates, so we publish the true layout size as
//   --layout-width / --layout-height for CSS, and getZoom() for JS.

const DESIGN_WIDTH = 1280 // CSS px the full layout is designed for
// Height the full layout needs: board + fixed recommendations bar measured ~796px.
const DESIGN_HEIGHT = 820
// Touch screens get ~40px-tall role buttons (two rows of them: grid filter + your role).
const TOUCH_EXTRA_HEIGHT = 40
const MIN_ZOOM = 0.3
const NARROW_MAX_WIDTH = 720 // layout px at or below which the phone layout applies
// Phones held sideways: the full design would scale to ~0.4 (tiny text and tap targets),
// so below COMPACT_BELOW they use a compact design on a smaller canvas instead.
const COMPACT_WIDTH = 960
const COMPACT_HEIGHT = 540
const COMPACT_BELOW = 0.75

let currentZoom = 1

export function getZoom(): number {
  return currentZoom
}

function apply() {
  const root = document.documentElement
  const finePointer = window.matchMedia('(pointer: fine)').matches
  const portraitTouch = !finePointer && window.innerHeight > window.innerWidth
  // Whichever dimension is tighter decides the scale (up or down).
  const designHeight = DESIGN_HEIGHT + (finePointer ? 0 : TOUCH_EXTRA_HEIGHT)
  let ratio = Math.min(window.innerWidth / DESIGN_WIDTH, window.innerHeight / designHeight)
  const compact = !finePointer && !portraitTouch && ratio < COMPACT_BELOW
  if (compact) {
    ratio = Math.min(window.innerWidth / COMPACT_WIDTH, window.innerHeight / COMPACT_HEIGHT)
  }
  const zoom = portraitTouch || ratio < MIN_ZOOM ? 1 : ratio
  currentZoom = zoom
  root.style.zoom = zoom === 1 ? '' : String(zoom)
  const layoutWidth = window.innerWidth / zoom
  const layoutHeight = window.innerHeight / zoom
  root.style.setProperty('--layout-width', `${layoutWidth}px`)
  root.style.setProperty('--layout-height', `${layoutHeight}px`)
  // narrow = portrait phone; compact = phone held sideways (bigger type/targets on a
  // smaller canvas, everything sized to fit one screen).
  if (layoutWidth <= NARROW_MAX_WIDTH) root.dataset.layout = 'narrow'
  else if (compact) root.dataset.layout = 'compact'
  else delete root.dataset.layout
}

export function installViewportScale() {
  apply()
  window.addEventListener('resize', apply)
}
