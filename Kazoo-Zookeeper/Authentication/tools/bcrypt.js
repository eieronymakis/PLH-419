const bcrypt = require('bcrypt');

const saltRounds = 10;

const getHash = async (_inp) => {
   let hash = await bcrypt.hash(_inp, saltRounds);
   if(hash){
    return hash
   }else{
    return -1
   }
}

const verify = async(_inp, _hash) => {
    let res = bcrypt.compare(_inp, _hash);
    return res;
}

module.exports = {getHash, verify};