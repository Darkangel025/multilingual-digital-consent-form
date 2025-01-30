// CreateForm.js
import React, { useState } from 'react';
import axios from 'axios';

const CreateForm = () => {
    const [patientName, setPatientName] = useState('');
    const [consentText, setConsentText] = useState('');
    const [language, setLanguage] = useState('en');

    const handleSubmit = (e) => {
        e.preventDefault();
        axios.post('/consent_form', {
            patient_name: patientName,
            consent_text: consentText,
            language: language
        }, {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }).then(response => {
            console.log(response.data);
        }).catch(error => {
            console.error(error);
        });
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="text" value={patientName} onChange={(e) => setPatientName(e.target.value)} placeholder="Patient Name" required />
            <textarea value={consentText} onChange={(e) => setConsentText(e.target.value)} placeholder="Consent Text" required></textarea>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
            </select>
            <button type="submit">Submit</button>
        </form>
    );
};

export default CreateForm;