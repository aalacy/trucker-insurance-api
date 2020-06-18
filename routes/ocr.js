module.exports = (app) => {
  let express = require('express')
  let multer  = require('multer')
  let router = express.Router();
  var path = require('path');
  const fetch = require('node-fetch');
  const env = process.env.NODE_ENV || 'development';
  const config = require(__dirname + '/../config/config.json')[env];
  const moment = require('moment');
  let model = require("../models/auto");
  let driverLicenseSnapshot = require('../utils/driver-license-snapshot.js');
  let ocr = require('../utils/ocr.js');
 
  var stoorages = multer.diskStorage({
    destination: function (req, file, cb) {
        // cb(null, 'public/company')
        cb(null, 'public/company');
    },
    filename: function (req, file, cb) {
        var ext;
        if(path.extname(file.originalname)== ""){
          ext = "."+file.mimetype;
        }else{
          ext = path.extname(file.originalname);
        }
        cb(null, file.fieldname + Date.now() + "-"+ext
        );
    }
  });

  let upload = multer({ storage: stoorages });
  const uuidv4 = require('uuid/v4');
  var fs = require('fs');

  router.post('/upload/dl', async (req, res, next) => {
    const { imageDL } = req.body
    let result;
    try{
      try {
        result = await ocr.dl(imageDL);
      } catch(e) {
        result = e
      }
      res.send(result)
    } catch(e){
      console.log(e);
      return res.send({
        status: "OK",
        data: e,
        messages: ['Accepted with an error']
      })
    }
  });

  router.post('/upload', upload.fields([
    {name: 'imageDL', maxCount: 1},
    {name: 'imageDOT', maxCount: 1},
    {name: 'imageVIN', maxCount: 1},
  ]), async (req, res, next) => {
    let uuid,result;

    if(Object.keys(req.files).length === 0){
      res.send({
        status: "OK",
        data: '',
        messages: ['no files, skip step']
      })
      return;
    }

    let log = {};
    Object.keys(req.files).forEach(async groupName => {
      try{
        if(!log[groupName])log[groupName] = {};

        Object.keys(req.files[groupName]).forEach(async file => {

          let theFile = req.files[groupName][file];
          console.log('Rw....', theFile.fieldname )

          if(theFile.fieldname === 'imageVIN'){
              try {
                result = await ocr.vin(theFile.path);
              } catch(e) {
                result = e
              }
          }  else if(theFile.fieldname === 'imageDOT'){
            try {
              result = await ocr.dot(theFile.path);
            } catch(e) {
              result = e
            }
          }

          console.log('Finished OCR', result);
          log[groupName][theFile.originalname] = result;
          res.send(result)
        })
      } catch(e){
        console.log(e);
        return res.send({
          status: "OK",
          data: e,
          messages: ['Accepted with an error']
        })
      }
    })
  })

  app.use('/api/ocr', router)
}