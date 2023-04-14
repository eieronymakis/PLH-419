const router = require('express').Router();
const jwt = require('jsonwebtoken');
const database = require('../tools/database');
const bcrypt = require('../tools/bcrypt');
require('dotenv').config();

router
    .route('/')
    .post(async(req,res) => {
        let {email, password} = req.body;
        let result = await database.executeQuery(`SELECT id,password FROM users WHERE email = '${email}'`);
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