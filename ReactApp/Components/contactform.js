import React from 'react';
import ReactDOM from 'react-dom';
import 'antd/dist/antd.css';
import './index.css';
import {
  Form,
  Input,
  Tooltip,
  Icon,
  Cascader,
  Select,
  Row,
  Col,
  Checkbox,
  Button,
  AutoComplete,
} from 'antd';

const { Option } = Select;
const AutoCompleteOption = AutoComplete.Option;

class ContactForm extends React.Component{
    render() {
        return (
            <form action="/edit_contact/{{ contact.contact_id }}" method="POST" id="edit_form{{ contactloop.index }}" class="hidden">
	        <b>Contact Name:</b> <input type=textbox name="name" value='{{ contact.name }}'></input><br>
	        <b>Phone Number:</b><input type="tel" name="phone" value="{{ contact.phone }}"><br>
	        <b>Email Address:</b><input type="email" name="email"><br>
	        <br>
	        <b>Custom Message For Contact</b>(Optional)<b>:</b><br>
	        <textarea rows="6" cols="50" name="message">{{ contact.c_message }}</textarea><br>


	        <button type="submit">Submit Changes</button>
</form>
        )
    }
}