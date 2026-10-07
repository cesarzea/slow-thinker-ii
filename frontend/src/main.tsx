import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import '@xyflow/react/dist/style.css';
import {App} from './app/app.tsx';

const container = document.getElementById('root');
if (container === null) throw new Error('The application container is missing.');
createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
