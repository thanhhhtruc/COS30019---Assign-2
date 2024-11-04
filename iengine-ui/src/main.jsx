import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import IEngineUI from './IEngineUI'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <IEngineUI /> {/* Render IEngineUI directly */}
  </StrictMode>,
)
