import React, { useState, useEffect, useRef } from 'react';

const EditorComponent = ({ username }) => {
  const [isTyping, setIsTyping] = useState(false);
  const [content, setContent] = useState('');
  const [currentTyping, setCurrentTyping] = useState('');
  const [filename, setFilename] = useState('file');
  const [fetchContent, setFetchContent] = useState("");
  const websocketRef = useRef(null);  // WebSocket reference to persist across renders

  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsTyping(false);
    }, 500);
    
    return () => clearTimeout(timeout);
  }, [content]);  // This runs every time 'content' changes


  useEffect(() => {
    // Open WebSocket connection based on the provided username
    websocketRef.current = new WebSocket(`ws://127.0.0.1:8000/ws/document/${username}`);

    websocketRef.current.onopen = () => {
      console.log(`WebSocket connection opened for document ${username}`);
    };

    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setContent(data.content); 
      setCurrentTyping(data.username);
      setIsTyping(true);
    };

    websocketRef.current.onclose = () => {
      console.log(`WebSocket connection closed for document ${username}`);
    };

    // Clean up WebSocket on component unmount
    return () => {
      websocketRef.current.close();
    };
  }, [username]);  // Re-run this effect if the 'username' changes

  useEffect(() => {
    setContent(fetchContent);
  }, [fetchContent]); 

  const handleInputChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    setIsTyping(true);
    setCurrentTyping(username);

    // Send updated content to the server via WebSocket
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      const data = JSON.stringify({
        action: 'edit',
        username: username,
        content: newContent
      });

      console.log(data);
      websocketRef.current.send(data);
    }
  };

  const handleFnameChange = (e) => {
    e.preventDefault();
    setFilename(e.target.value);
  }

  const handleSaveDb = async () => {
    try {
      const response = await fetch('https://sharededitor-server.onrender.com/save-to-db', {
      //const response = await fetch('http://127.0.0.1:8000/save-to-db', {
        method:'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, content }),
      });
      if (response.ok) {
        alert("Content saved:", content);
      } else {
        alert("Failed to save");
      }
    } catch (error) {
        console.error("Error saving:", error);
        alert("Error while saving");
    }
  }

  const handleGetDb = async () => {
    try {
      const response = await fetch(`https://sharededitor-server.onrender.com/load-from-db?username=${username}`, {
      // const response = await fetch(`http://127.0.0.1:8000/load-from-db?username=${username}`, {
        method:'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json(); 
        if (data.success) {
          setContent(data.content); 
        } else {
          alert(data.message);
        }
        window.location.reload();
      } else {
        alert("Nothing found!");
      }
    } catch (error) {
      console.error("Error Getting Data:", error);
      alert("Error while getting data from db");
    }
  }

  // When Save to File is clicked, downloads the contents of the editor into a new .txt file named after what the filename state is
  const handleExport = () => {
    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const newName = filename + '.txt';
    link.setAttribute('download', newName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <div style={{display: 'flex', flexDirection: 'column', alignContent: 'center', justifyContent: 'center', width: '400px'}}>
        <input type="text" value={filename} onChange={handleFnameChange}/>
        <textarea
          id="editor"
          value={content}
          onChange={handleInputChange}
          placeholder="Start typing..."
          rows="10"
          cols="50"
        />
        {isTyping ? (
          <p> {currentTyping} is typing ... </p>
        ) : (
          <>
              <p>Waiting for input ...</p>
            </>
        )}
      </div>
      <button onClick={handleSaveDb}>Save to DB</button>
      <button onClick={handleExport}>Save To File</button>
      <button onClick={handleGetDb}>Retrieve From DB</button>


    </div>
  );
};

export default EditorComponent;
