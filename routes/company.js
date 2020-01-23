module.exports = (app) => {
  var webConfig = require("../config/web.js");
  let express = require('express')
  let multer  = require('multer')
  let router = express.Router();
  var path = require('path');
  var pdf = require('html-pdf');
  
  //  let upload = multer({ dest: webConfig.rootDir+'/public/company/' })
  //let upload = multer({ dest: "http://3.13.68.92:3000/public/company/"})
  
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

let upload = multer({
    storage: stoorages
});
  let document = require('../models/Document')
  const vision = require('@google-cloud/vision')
  const client = new vision.ImageAnnotatorClient()
  let visionUtil = require('../utils/Vision')
  let companySnapshot = require('../utils/company-snapshot')
  let vehicleTitleSnapshot = require('../utils/vehicle-title-snapshot.js');
  let driverLicenseSnapshot = require('../utils/driver-license-snapshot.js');
  let checkr = require('../utils/Checkr')
  let responseHelper = require('../helpers/string')
  const uuidv4 = require('uuid/v4');
  let model = require("../models/auto");
  var fs = require('fs');
  const LookupVehicle = require('lookup_vehicle');
  const parseAddress = require('parse-address');
  let pdfApplication = require('../utils/pdf-application');


  //UPDATE `test` SET `value` = JSON_SET(`value`, '$."key 1"', 'value 1', '$.c', '[true, false]') WHERE `key` = 'first'

  router.get('/pdf', async (req, res, next) => {
    let uuid;
    if(req.query.uuid)uuid = req.query.uuid;
    else if(req.body.uuid)uuid = req.body.uuid;
    else if(req.cookies.uuid)uuid = req.cookies.uuid;

    if(!uuid){
      res.send({
        status: "OK",
        data: 'uuid is empty',
        messages: []
      })
      return;
    }

    pdfApplication.get(uuid, 0, new model.Company()).then(location => {
      console.log('pdfApp:'+ JSON.stringify(location));
      if(req.body.email == undefined){
        fs.readFile(location, function (err,data){
          // console.log('FsData:'+ JSON.stringify(data));
           res.contentType("application/pdf");
           res.send(data);
         });
      }else{
        res.send({
          status: "Success",
          data: JSON.stringify(location),
          messages: "success"
        })
      }

    }).catch(err => {
      res.send({
        status: "ERROR",
        data: 'find by uuid',
        messages: err
      })
    })
  })

  router.all('/pdf-preview', async (req, res, next) => {

    let uuid;
    if(req.query.uuid)uuid = req.query.uuid;
    else if(req.body.uuid)uuid = req.body.uuid;
    else if(req.cookies.uuid)uuid = req.cookies.uuid;

    if(!uuid){
      res.send({
        status: "OK",
        data: 'uuid is empty',
        messages: []
      })
      return;
    }

    pdfApplication.getHTML(uuid, new model.Company()).then(html => {

        res.send(html);

    }).catch(err => {
      res.send({
        status: "ERROR",
        data: 'find by uuid',
        messages: err
      })
    })
  })

  router.all('/vin', async (req, res, next) => {

    if (!req.body.vin && !req.query.vin) {
      return res.send({
          status: "ERROR",
          data: {},
          messages: ['vin is empty']
      })
    }

    let vin = (req.body.vin)?req.body.vin:req.query.vin;
    try{
      let result = await LookupVehicle.lookup(vin);

      let vehiclesTrailers = { model: ''};
      if(result.data && result.data.Results){
        vehiclesTrailers.raw = result.data.Results;
        if(result.data.Results[0].VIN){
          vehiclesTrailers.VIN = result.data.Results[0].VIN;
          vehiclesTrailers.vehicleHistory = await vehicleTitleSnapshot.getVehicleHistory(vehiclesTrailers.VIN);
        }
        if(result.data.Results[0].ModelYear)vehiclesTrailers.year = result.data.Results[0].ModelYear;
        if(result.data.Results[0].Make)vehiclesTrailers.make = result.data.Results[0].Make;
        if(result.data.Results[0].Model)vehiclesTrailers.model = result.data.Results[0].Model;
        if(result.data.Results[0].VehicleType)vehiclesTrailers.vehicleType = result.data.Results[0].VehicleType;
      }

      res.send({
        status: "OK",
        data: vehiclesTrailers,
        messages: []
      })


    }catch(e){
      res.send({
        status: "ERROR",
        data: e,
        messages: []
      })
    }

  })

  router.all('/search', async (req, res, next) => {

      if (!req.body.keyword && !req.query.keyword) {
        return res.send({
            status: "ERROR",
            data: {},
            messages: ['keyword is empty']
        })
      }

      let keyword = (req.body.keyword)?req.body.keyword:req.query.keyword;
      let so;
      if(!isNaN(keyword)){
        so = await companySnapshot.get(keyword).catch(err => console.log(err));
      }else{
        so = await companySnapshot.search(keyword).catch(err => console.log(err));
      }
      if (so) {
        res.send({
            status: "OK",
            data: so,
            messages: []
        })
      } else {
        res.send({
            status: "Error",
            messages: ["No search results"]
        })
      }
  })

  router.all('/create', async (req, res, next) => {

    if (!req.body.usdot && !req.query.usdot) {
      return res.send({
          status: "ERROR",
          data: {},
          messages: ['usdot is empty']
      })
    }
    let usdot = (req.body.usdot)?req.body.usdot:req.query.usdot;
    let company = await companySnapshot.get(usdot);
    let uuid = await getNewUUID();

    if(company['USDOT Number'] !== usdot){
      res.send({
        status: "ERROR",
        data: company,
        messages: ['exact company not found']
      })
      return;
    }

    let businessStructure = {}
    if(company){
      const name = company['Legal Name'];
      const dotNumber = company['USDOT Number'];
      const dba = company['DBA Name'];
      const phoneNumber = company['Phone'];
      const mailingAddress = {};
      const garagingAddress = {};
      const emailAddress = "";
      const mcNumber = company['MC/MX/FF Number(s)'];
      const currentCarrier = company['Carrier Operation'];
      const travelRadius = "";
      const currentEldProvider = [];
      const cargoHauled = {};
      const powerUnits =  company['Power Units'];
      const businessType = '';
      const businessStructure = '';


      if(company["Mailing Address"]){
        let tmp = new model.Company().parseAndAssignAddress(company["Mailing Address"], {}, '');
        Object.keys(tmp).forEach(function(key) {
          let _key = key.replace('address', 'street');
          mailingAddress[_key] = tmp[key];
        });
      }

      if(company["Physical Address"]){
        let tmp = new model.Company().parseAndAssignAddress(company["Physical Address"], {}, '');
        Object.keys(tmp).forEach(function(key) {
          garagingAddress[key] = tmp[key];
        });
      }
      const options = {
        businessStructureRaw: company,
        name,
        dotNumber,
        dba,
        phoneNumber,
        mailingAddress,
        garagingAddress,
        emailAddress,
        mcNumber,
        currentCarrier,
        travelRadius,
        currentEldProvider,
        cargoHauled
      }
      await new model.Company().create(uuid, options );

      res.cookie('uuid', uuid, { maxAge: 9000000, httpOnly: false });
      new model.Company().findByUUID(uuid).then(profile => {
        // console.log('company profile in create '+ JSON.stringify(profile));

        res.send({
            status: "OK",
            //data: new model.Company().renderAllByType(profile),
            data:company, //b
            messages: []
          })
      }).catch(err => {
        console.log('Err:'+err);
        res.send({
          status: "ERROR",
          data: 'can not create new company',
          messages: err
        })
      })
    } else {
      res.send({
        status: "ERROR",
        data: 'can not create new company',
        messages: 'can not create new company'
      })
    }
  })


  async function getProfile(uuid){
    return new Promise((resolve, reject) => {
      new model.Company().findByUUID(uuid).then(profile => {
          resolve(profile)
      }).catch(err => {
          resolve(false)
      })
    })
  }

  async function getNewUUID(attemp = 0){
    return new Promise((resolve, reject) => {

      uuid = uuidv4();
      new model.Company().findByUUID(uuid).then(profile => {
          if(profile){
            getNewUUID(attemp + 1)
          }else{
            resolve(uuid)
          }
          
      }).catch(err => {
          reject(err)
      })

    })
  }


  router.all('/current', async (req, res, next) => {

    let uuid;
    if(req.query.uuid)uuid = req.query.uuid;
    else if(req.body.uuid)uuid = req.body.uuid;
    else if(req.cookies.uuid)uuid = req.cookies.uuid;
    
    if (uuid) {
      new model.Company().findByUUID(uuid).then(company => {
        console.log('profile Current in /current:' + JSON.stringify(company));
        res.send({
          status: "OK",
          data: {
            company,
            uuid,
          },
          messages: []
        })
    }).catch(err => {
      res.send({
        status: "ERROR",
        data: 'find by uuid',
        messages: err
      })
    })

    }else{
      res.send({
        status: "ERROR",
        data: 'uuid is empty',
        messages: []
      })
    }

  })



  router.all('/hubspot', async (req, res, next) => {
    console.log("hubspot1 req",req);
    console.log("hubspot1 res",res);
    console.log("hubspot1 next",next);   
    let uuid, error, log;

    if(req.query.uuid)uuid = req.query.uuid;
    else if(req.body.uuid)uuid = req.body.uuid;
    else if(req.cookies.uuid)uuid = req.cookies.uuid;
    
    if (!uuid) {
      console.log("hubspot uuid is not found",!uuid)
      res.send({
        status: "ERROR",
        data: 'uuid is empty',
        messages: []
      });
      return;
    }
    console.log("hubspot2 if uuid")


      try{
        log = await new model.Company().updateHubspot(uuid);
        console.log('Update hubspot',log)
        res.send({
          status: "OK",
          data: log,
          messages: []
        })
      }catch(e){
        console.log("Update hubspot error",e)
        res.send({
          status: "ERROR",
          data: e,
          messages: []
        })
      }

  })

  // router.post('/upload',async (req, res, next) => {
  //   console.log("test");
  //   res.send("test").end();
  // });
 

  router.post('/upload', upload.fields([
    {name: 'imageIdFront', maxCount: 1},
    {name: 'imageIdBack', maxCount: 1},
    {name: 'imageDOT', maxCount: 1},
    {name: 'imageRegistration', maxCount: 1},
    {name: 'lossRun', maxCount: 1},
    {name: 'ifta', maxCount: 1},
    {name: 'contracts', maxCount: 1},
    {name: 'declarations', maxCount: 1},
    {name: 'rentalLeaseAgreement', maxCount: 1},
    {name: 'previouslyCompletedApplications', maxCount: 1},
    {name: 'insuranceRequirements', maxCount: 1},
    {name: 'imageSign', maxCount: 1},
    
    
  ]), async (req, res, next) => {
    let doc = new document()

    let uuid,result;

    if(Object.keys(req.files).length === 0){
      res.send({
        status: "OK",
        data: '',
        messages: ['no files, skip step']
      })
      return;
    }

    if(req.query.uuid)uuid = req.query.uuid;
    else if(req.body.uuid)uuid = req.body.uuid;
    else if(req.cookies.uuid)uuid = req.cookies.uuid;

    if(!uuid)uuid = await getNewUUID();

    res.cookie('uuid',uuid, { maxAge: 9000000, httpOnly: false });
    

    
    let headersSent = false;
    let filesApproved = 0;

    let log = {};

    Object.keys(req.files).forEach(async groupName => {
      try{
        console.log('.........'+ groupName)
            await new model.Company().add(uuid, groupName, req.files[groupName], false);

            if(!log[groupName])log[groupName] = {};

            Object.keys(req.files[groupName]).forEach(async file => {

              let theFile = req.files[groupName][file];
              /*{ fieldname: 'imageRegistration',
              originalname: '20190412_154247--.jpg',
              encoding: '7bit',
              mimetype: 'image/jpeg',
              destination: 'public/company/',
              filename: 'fbbd26d530b42ecdf1a43bacc134e705',
              path: 'public/company/fbbd26d530b42ecdf1a43bacc134e705',
              size: 3351277 }*/
              console.log('Rw....',theFile.fieldname)

              if(theFile.fieldname === 'imageRegistration'){
                  try{
                    result = await vehicleTitleSnapshot.scan(theFile.path);
                    
                    if(result.vin){
                        let vehiclesTrailers = {}
                        if(result.vin)vehiclesTrailers.VIN = result.vin;
                        if(result.VINDetails.ModelYear)vehiclesTrailers.year = result.VINDetails.ModelYear;
                        if(result.VINDetails.Make)vehiclesTrailers.make = result.VINDetails.Make;
                        if(result.VINDetails.Model)vehiclesTrailers.model = result.VINDetails.Model;
                        if(result.VINDetails.VehicleType)vehiclesTrailers.vehicleType = result.VINDetails.VehicleType;
                        await new model.Company().add(uuid, 'vehiclesTrailers', [vehiclesTrailers]);
                        log[groupName][theFile.originalname] = vehiclesTrailers;
                    }else{
                      log[groupName][theFile.originalname] = 'VIN not found';
                    }
                  }catch(e){
                    log[groupName][theFile.originalname] = e;
                  }
              }else if(theFile.fieldname === 'imageIdFront'){
                console.log('p.........',theFile.path);
                    result = await driverLicenseSnapshot.scan(theFile.path);
                    console.log('p.........',result);
                    await new model.Company().add(uuid, 'personalInfo', result, false);
                    await new model.Company().add(uuid, 'drivers', [result], true);
                    log[groupName][theFile.originalname] = result;
              }else if(theFile.fieldname === 'imageSign'){
                
                console.log('p.........',theFile.path);
              
                let dt = new Date().toISOString().slice(0,10);
                console.log("dt",dt)
                  new model.Company().add(uuid, 'imageSign').then(profile => {
                   console.log('prrrrrrr',profile)
                  }).catch(err => {
                    console.log('eerr', err);
                   
                  })
              }
              else{
                    log[groupName][theFile.originalname] = 'saved';
              }


              //console.log('*****',Object.keys(req.files).length,'******');
              filesApproved++;
              if(!headersSent && filesApproved>= Object.keys(req.files).length){
                headersSent = true;
                res.send({
                  status: "OK",
                  data: log,
                  messages: ['Accepted']
                })
              }


            })

      }catch(e){
        console.log(e);

        res.send({
          status: "OK",
          data: e,
          messages: ['Accepted with an error']
        })

        return;
      }

    })


  })


router.post('/uploadSign', upload.single('imageSign'),async(req,res,next)=>{
  console.log('mmmmmmmmmm',req.val);
  console.log('iiiiiiiiiiii',req.imageSign);

  let uuid;
  if(req.cookies.uuid)uuid = req.cookies.uuid;
let dt = new Date('dd-mm-yyyy');
let obj ={
  filePath:'',
  date:dt.getDate()
}
  new model.Company().add(uuid, 'imageSign',dt.getDate()).then(profile => {
    res.send({
      status: "OK",
      data: profile,
      messages: profile.dataValues
    })
  }).catch(err => {
    console.log('eerr', err);
    res.send({
      status: "ERROR",
      data: uuid,
      messages: err
    })
  })
})

  router.post('/save', async (req, res, next) => {

    let profile;

    const { data } = req.body;
    let uuid = data.uuid;
    if (!uuid && req.cookie) {
      const { uuid } = req.cookie;
    }

    if (!uuid) {
      uuid = await getNewUUID();
    }

    res.cookie('uuid', uuid, { maxAge: 9000000, httpOnly: false });

    // Update salesforce if this the last step, sign signature, of form wizard
    if (data.signSignature) {

    }

    new model.Company().create(uuid, data).then(profile => {
      res.send({
        status: "OK",
        data: uuid,
        messages: profile.dataValues
      })
    }).catch(err => {
      console.log('err in save company', err);
      res.send({
        status: "ERROR",
        data: uuid,
        messages: err
      })
    })

  })

  app.use('/api/company', router)
}
