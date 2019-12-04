import React from 'react';
import { Contact } from './contact';
import { prefix } from "../urlprefix"

export class Contacts extends React.Component{
    componentWillMount() {
        let uri = prefix + "/contacts"
        fetch(url, {
            method: 'post',
            body: formData,
        });
      }
    render() {
        const contacts = {% contacts %}
        return(      
        )
    }
}