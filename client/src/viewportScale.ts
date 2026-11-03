// Scales the whole page down (CSS `zoom` on <html>) when a desktop window is
// narrower than the layout was designed for, so a small window looks like a
// shrunken copy of the full-size page instead of a cramped, "zoomed-in" one.
//
// - Mouse/trackpad devices only (`pointer: fine`): phones and tablets keep zoom 1
//   and use the responsive layout instead.
// - Never scales below MIN_ZOOM: windows narrower than DESIGN_WIDTH * MIN_ZOOM
//   (640px) get zoom 1 and the responsive layout instead.
// - Media and container queries also measure in window (zoomed) px, so the narrow
//   (phone) layout is switched by a data-layout="narrow" attribute on <html>,
//   decided here from the true layout width; likewise data-layout="short" for
//   short screens (landscape phones) from the true layout height.
// - Under `zoom`, `vw`/`vh` are NOT compensated and getBoundingClientRect()
//   returns zoomed (visual) coordinates, so we publish the true layout size as
//   --layout-width / --layout-height for CSS, and getZoom() for JS.

const DESIGN_WIDTH = 1280 // CSS px the full layout is designed for
const MIN_ZOOM = 0.5
const NARROW_MAX_WIDTH = 720 // layout px at or below which the phone layout applies
const SHORT_MAX_HEIGHT = 500 // layout px at or below which the short (landscape-phone) layout applies

let currentZoom = 1

export function getZoom(): number {
  return currentZoom
}

function apply() {
  const root = document.documentElement
  const finePointer = window.matchMedia('(pointer: fine)').matches
  const ratio = window.innerWidth / DESIGN_WIDTH
  // Below MIN_ZOOM the scaled page would be unreadably small: use zoom 1 and let
  // the responsive (narrow) layout take over instead.
  const zoom = finePointer && ratio >= MIN_ZOOM ? Math.min(1, ratio) : 1
  currentZoom = zoom
  root.style.zoom = zoom === 1 ? '' : String(zoom)
  const layoutWidth = window.innerWidth / zoom
  const layoutHeight = window.innerHeight / zoom
  root.style.setProperty('--layout-width', `${layoutWidth}px`)
  root.style.setProperty('--layout-height', `${layoutHeight}px`)
  // narrow = portrait phone; short = landscape phone (or any very short window):
  // compact board that fits the screen, recommendations scroll below it.
  if (layoutWidth <= NARROW_MAX_WIDTH) root.dataset.layout = 'narrow'
  else if (layoutHeight <= SHORT_MAX_HEIGHT) root.dataset.layout = 'short'
  else delete root.dataset.layout
}

export function installViewportScale() {
  apply()
  window.addEventListener('resize', apply)
}
