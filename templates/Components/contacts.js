import React from 'react';
import { Contact } from './contact';
import { prefix } from "../urlprefix"

export class Contacts extends React.Component{
    componentWillMount() {
        let uri = prefix + "/view_contacts"
        const response = await fetch(uri);
        const myJson = await response.json();
        console.log(JSON.stringify(myJson));
      }
    render() {
        return(      
        )
    }
}