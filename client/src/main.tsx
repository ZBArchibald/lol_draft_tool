import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Marker & Carpet theme: tokens -> carpet background -> mc-* components -> app styles.
import './theme/tokens.css'
import './theme/background.css'
import './theme/bundle.css'
import './index.css'
import Carpet from './components/Carpet.tsx'
import App from './App.tsx'
import { installViewportScale } from './viewportScale'

// Shrink the page proportionally in small desktop windows (before first paint).
installViewportScale()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Carpet />
    <App />
  </StrictMode>,
)
