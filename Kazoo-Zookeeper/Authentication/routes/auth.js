const router = require('express').Router();
const jwt = require('jsonwebtoken');
const database = require('../tools/database');
const bcrypt = require('../tools/bcrypt');
require('dotenv').config();

router
    .route('/')
    .post(async(req,res) => {
        let {username, password} = req.body;
        console.log(username+" "+password)
        let result = await database.executeQuery(`SELECT id,password FROM users WHERE username = '${username}'`);
        if ( result.length == 0 ){
            res.status(404).end()
        }
        let hash = result[0].password;
        let id = result[0].id;
        let correct = await bcrypt.verify(password,hash);
        if(correct){
            let token = jwt.sign({id:id},process.env.JWT_SECRET);
            res.send({Token:token}).status(200).end()
        }else{
            res.send({Message:'Credentials incorrect'}).status(401).end()
        }
    })

module.exports = router;