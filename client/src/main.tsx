import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Marker & Carpet theme: tokens -> carpet background -> mc-* components -> app styles.
import './theme/tokens.css'
import './theme/background.css'
import './theme/bundle.css'
import './index.css'
import Carpet from './components/Carpet.tsx'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Carpet />
    <App />
  </StrictMode>,
)
