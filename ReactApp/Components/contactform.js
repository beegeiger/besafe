import React from 'react';
import 'antd/dist/antd.css';
import { prefix } from "../urlprefix"
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

export class ContactForm extends React.Component{
    handleSubmit(e) {
        e.preventDefault();
        var formData = new FormData(form)
        let uri = "prefix" + "/contacts"
        fetch(url, {
            method: 'post',
            body: formData,
        })
    }
    render() {
        return (
            <div>
            <form>
                <b>Contact Name:</b> <input type='textbox' name="name"></input>
                <b>Phone Number:</b><input type="tel" name="phone"></input>
                <b>Email Address:</b><input type="email" name="email"></input>
                <b>Custom Message For Contact</b>(Optional)<b>:</b><br />
                <textarea rows="6" cols="50" name="message"></textarea>
                <button type="submit">Save Contacts</button>
            </form>
            </div>
        )
    }
}