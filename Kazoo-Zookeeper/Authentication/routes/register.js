const router = require('express').Router();
const bcrypt = require('../tools/bcrypt');
const database = require('../tools/database');
require('dotenv').config();

router
    .route('/')
    .post(async(req,res)=>{
        let {email, password, role, username} = req.body;
        if(role!=='user' && role !=='admin'){
            res.send({Message:'Role should be admin/user (case sensitive)'}).status(400).end();
        }else{
            let hash = await bcrypt.getHash(password);
            if(hash!=-1){
                let result = await database.executeQuery(`SELECT COUNT(username) AS count FROM users WHERE username = '${username}'`);
                if(result[0].count > 0){
                    res.send({Message:'User already exists'}).status(409).end();
                }else{
                    result = await database.executeQuery(`INSERT INTO users (email, password, role, username) values ('${email}', '${hash}', '${role}', '${username}' )`);
                    if(result.affectedRows > 0)
                        res.status(201).end();
                    else{
                        res.status(400).end();
                    }
                }
                res.status(200).end();
            }else{
                res.status(500).end()
            }
        }
    })  



module.exports = router;