const mysql = require('mysql2')

let con = mysql.createConnection({
    host: "localhost",  
    port: 3306,
    user: "root",
    database: "auth_svc",
    password: "xyz123",
	charset : 'utf8mb4'
});      
       
con.connect(function(err){
    if(err){
        console.log('--------------------------------------');
        console.log('Database Connection -> False');
        console.log('--------------------------------------');
	throw err;
        process.exit();
    }
    console.log('--------------------------------------');
    console.log('Database Connection -> True');
    console.log('--------------------------------------');
});

module.exports = {
    /*---------------------------------------------------  
                EXECUTES QUERY AND RETURNS DATA (ASYNC)
    ---------------------------------------------------*/
    executeQuery(query){
        return new Promise((resolve, reject) => {
            con.query(query, (err, result) => {
                if(err){
                    reject(err);
                } else {
                    resolve(result);
                }
            })
        });
    },
}