import { useState } from 'react';

function App() {
  const [input, setInput] = useState('');
  const [reply, setReply] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      setReply(data.reply);
    } catch (err) {
      setReply('⚠️ Error: ' + err.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: 'auto' }}>
      <h1> Chatbot Web</h1>
      <textarea
        value={input}
        onChange={e => setInput(e.target.value)}
        rows={5}
        placeholder="Напиши сообщение..."
        style={{ width: '100%', marginBottom: '1rem' }}
      />
      <br />
      <button onClick={sendMessage} disabled={loading}>
        {loading ? 'Отправка...' : 'Отправить'}
      </button>
      {reply && (
        <div style={{ marginTop: '2rem' }}>
          <strong>Ответ:</strong>
          <p>{reply}</p>
        </div>
      )}
    </div>
  );
}

export default App;
