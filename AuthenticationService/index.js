const express = require('express');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended:true }));

var allowCrossDomain = function(req, res, next) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS');
  res.header('Access-Control-Allow-Headers', '*');
  next();
}
app.use(allowCrossDomain)

app.use('/auth', require('./routes/auth'));
app.use('/register', require('./routes/register'));

app.get('/', (req, res) => {
  res.send({ message: 'Welcome to Authentication Service' });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
}); 