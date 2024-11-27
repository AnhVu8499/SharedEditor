import React, { useState } from 'react';
import EditorComponent from './components/EditorComponent';
import Login from './components/Login';
import SignUp from './components/SignUp';

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false); 
    const [username, setUsername] = useState(''); 
    const [password, setPassword] = useState('');

    const handleLogin = (loginStatus, username) => {
        setIsLoggedIn(loginStatus); 
        setUsername(username);
    };
    const handleSignUp = ( username, password ) =>{
        setUsername(username);
        setPassword(password);
    }

    return (
        <div>
            <SignUp onSignUp={handleSignUp}/>
            {!isLoggedIn ? (
                <Login onLogin={handleLogin} />
            ) : (
                <>
                    <h1>Welcome, {username}!</h1>
                    <EditorComponent username={username} /> 
                </>
            )}
        </div>
    );
};

export default App;
