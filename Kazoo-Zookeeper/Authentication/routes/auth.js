const router = require('express').Router();
const jwt = require('jsonwebtoken');
const database = require('../tools/database');
const bcrypt = require('../tools/bcrypt');
const e = require('express');
require('dotenv').config();

router
    .route('/')
    .post(async(req,res) => {
        let {username, password} = req.body;

        if(username === undefined || password === undefined)
            res.status(400).end()
        else{
            let result = await database.executeQuery(`SELECT id,password,username FROM users WHERE username = '${username}'`);
            if ( result.length == 0 )
                res.status(404).end()
            else{
                let hash = result[0].password;
                let id = result[0].id;
                let username = result[0].username;
                let token_info = {id:id, username:username}
                let correct = await bcrypt.verify(password,hash);
                if(correct){
                    let token = jwt.sign(token_info,process.env.JWT_SECRET);
                    res.send({Token:token}).status(200).end()
                }else{
                    res.send({Message:'Credentials incorrect'}).status(401).end()
                }
            }
        }
    })

module.exports = router;