module.exports = (app) => {
  let express = require('express')
  let multer  = require('multer')
  let router = express.Router();
  var path = require('path');
  const fetch = require('node-fetch');
  const env = process.env.NODE_ENV || 'development';
  const config = require(__dirname + '/../config/config.json')[env];
  const publicIp = require('public-ip');
  var geoip = require('geoip-lite');
  
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


  // Authentication to Salesforce
  const authSalesforce = async () => {
    return await fetch(`https://${config.sf_server}.salesforce.com/services/oauth2/token?grant_type=password&client_id=${config.sf_client_id}&client_secret=${config.sf_client_secret}&username=${config.sf_username}&password=${config.sf_password}`, { method: 'POST', headers: {'Content-Type': 'application/json'} })
                  .then(res => res.json()) // expecting a json response
                  .then(json => json);
  }

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
      if (Object.keys(so).length !== 0 && so.constructor === Object) {
        let _address = so['Physical Address'].split(' ');
        const index = _address.length;
        let data = [{
          name: so['Legal Name'],
          usdot: so['USDOT Number'],
          location: `${_address[index-4]} ${_address[index-3]}`
        }]
        res.send({
            status: "OK",
            type: 'USDOT',
            data: data,
            message: ""
        })
      } else {
        res.send({
            type: "USDOT",
            status: "Error",
            message: 'If your company is new, feel welcome to call us at <a href="tel:15135062400 " style="color: rgb(0, 123, 255); font-weight: bold; white-space: nowrap;">1-513-506-2400</a> and we can help set up your authority, otherwise check the number and search again.'
        })
      }
    }else{
      so = await companySnapshot.search(keyword).catch(err => console.log(err));
      const clientIp = await publicIp.v4()
      var geo = geoip.lookup(clientIp);
      let filteredData = so.filter(item => item.location.split(',')[1].trim() == geo.region);
      let new_data = filteredData || [];
      so.map(item => {
        if (!new_data.includes(item)) {
          new_data.push(item);
        }
      })
      if (new_data.length !== 0) {
        res.send({
            status: "OK",
            data: new_data,
            message: ""
        })
      } else {
        res.send({
            status: "Error",
            message: 'No company found. If you\'re company is new please call <a href="tel:15135062400 " style="color: rgb(0, 123, 255); font-weight: bold; white-space: nowrap;">1-513-506-2400</a> or click <a href="/account-info" style="color: rgb(0, 123, 255); font-weight: bold; white-space: nowrap;">here </a> to complete your application.'
        })
      }
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

  router.post('/accountinfo/policies', async (req, res, next) => {
    const { body: { DOT_ID } } = req;

    const authSF = await authSalesforce();
    let accessToken = authSF.access_token;
    let instanceUrl = authSF.instance_url;       
    let sfReadAccountPoliciesUrl = `${instanceUrl}/services/apexrest/account/policy`;
    const sfRequestBody = {
      "DOT Id": DOT_ID
    }

    let sfCARes = await fetch(sfReadAccountPoliciesUrl, { method: 'POST', body: JSON.stringify(sfRequestBody), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                  .then(res => res.json()) // expecting a json response
                  .then(json => json);

    if (sfCARes.status == 'Success') {
      res.json({
        status: "ok",
        policies: sfCARes.policies
      })
    } else {

    }
  });

  app.use('/api/company', router)
}
