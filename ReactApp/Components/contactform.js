import React from 'react';
import 'antd/dist/antd.css';
import { prefix } from "../urlprefix"
import { createForm } from "rc-form";

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
        const  getFieldDecorator  = this.props.form;
        const  autoCompleteResult  = this.state;
        return (
            <div>
                {/* <Form>
                    <Form.Item label="Contact Name">
                        {getFieldDecorator('name', {
                            rules: [
                            {
                                type: 'string',
                                message: 'You Must add a Contact Name!',
                            },
                            {
                                required: true,
                                message: 'You Must add a Contact Name!',
                            },
                            ],
                        })(<Input />)}
                    </Form.Item>
                    <Form.Item label="E-mail">
                        {getFieldDecorator('email', {
                            rules: [
                            {
                                type: 'email',
                                message: 'The input is not valid E-mail!',
                            },
                            {
                                required: false,
                                message: 'Please input contact E-mail!',
                            },
                            ],
                        })(<Input />)}
                    </Form.Item>
                    <Form.Item label="Phone Number">
                        {getFieldDecorator('phone', {
                            rules: [{ required: false, message: 'Please input your contact number!' }],
                        })(<Input addonBefore={prefixSelector} style={{ width: '100%' }} />)}
                    </Form.Item>
                </Form> */}

            <form>
                <b>Contact Name:</b> <input type='textbox' name="name"></input><br />
                <b>Phone Number:</b><input type="tel" name="phone"></input><br />
                <b>Email Address:</b><input type="email" name="email"></input><br />

                {/* <textarea rows="6" cols="50" name="message"></textarea> */}
                <button type="submit">Save Contact</button>
            </form>
            </div>
        )
    }
}

// export const WrappedContactForm = createForm()(ContactForm);