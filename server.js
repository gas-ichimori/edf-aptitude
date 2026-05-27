const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

let appState = {
  character: 'soldier',
  background: 'bg1',
};

let sseClients = [];

app.get('/api/state', (req, res) => {
  res.json(appState);
});

app.get('/api/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();
  sseClients.push(res);
  req.on('close', () => {
    sseClients = sseClients.filter(c => c !== res);
  });
});

app.post('/api/settings', (req, res) => {
  const { character, background } = req.body;
  if (character && ['soldier', 'professor'].includes(character)) appState.character = character;
  if (background && ['bg1', 'bg2'].includes(background)) appState.background = background;
  const msg = JSON.stringify({ type: 'settings-changed', ...appState });
  sseClients.forEach(c => c.write(`data: ${msg}\n\n`));
  res.json(appState);
});

app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`EDF診断: http://localhost:${PORT}`));
