import React, { useState } from 'react'

function SignUp() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')

    function handleSubmit(e) {
        e.preventDefault()
        console.log(username)
        console.log(password)
    }

    return (
        <div className='signUp'>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Username</label>
                    <input type='text' value={username} onChange={(input) => setUsername(input.target.value)}/>
                </div>
                <div>
                    <label>Password</label>
                    <input type='text' value={password} onChange={(input) => setPassword(input.target.value)}/>
                </div>
                <button type='submit'>Sign Up</button>
            </form>
        </div>
    )
}

export default SignUp;