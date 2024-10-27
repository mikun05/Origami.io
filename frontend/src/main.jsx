import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import CreaseLoader from './components/CreaseLoader'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CreaseLoader />
  </StrictMode>,
)
