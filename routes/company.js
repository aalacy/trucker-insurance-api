module.exports = (app) => {
  let express = require('express')
  let multer  = require('multer')
  let router = express.Router();
  var path = require('path');
  const fetch = require('node-fetch');
  const env = process.env.NODE_ENV || 'development';
  const config = require(__dirname + '/../config/config.json')[env];
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
  const LookupVehicle = require('lookup_vehicle');
  const parseAddress = require('parse-address');
  const { exec } = require("child_process");
  const moment = require('moment');
  const pdf2base64 = require('pdf-to-base64');
  const vision = require('@google-cloud/vision')
  const client = new vision.ImageAnnotatorClient()
  let visionUtil = require('../utils/Vision')
  let companySnapshot = require('../utils/company-snapshot')
  let vehicleTitleSnapshot = require('../utils/vehicle-title-snapshot.js');
  let driverLicenseSnapshot = require('../utils/driver-license-snapshot.js');
  let document = require('../models/Document')
  let checkr = require('../utils/Checkr')
  let responseHelper = require('../helpers/string')
  let model = require("../models/auto");
  let pdfApplication = require('../utils/pdf-application');
  let pdfCOI = require('../utils/pdf_coi');
  var webConfig = require("../config/web.js");

  // get Geo data
  const getGeoData = async (coords) => {
    coords = JSON.parse(coords);
    const data = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${coords['lat']}, ${coords['lng']}&key=${config.google_api}`)
        .then(res => res.json()) // expecting a json response
        .then(json => json);
    let state = ''
    if (data['results'].length > 0) {
      const result = data['results'][0];
      result['address_components'].forEach(item => {
        if (item.types.includes('administrative_area_level_1')) {
          state = item.short_name;
        }
      })
    }

    return state;
  }

  router.post('/coi/new', async (req, res, next) => {
    const { certData, userId } = req.body;

    const authSF = await new model.User().getSFToken(userId);
    let accessToken = authSF.access_token;
    let instanceUrl = authSF.instance_url;       
    let sfNewCOIUrl = `${instanceUrl}/services/apexrest/luckytruck/coi?type=new`;

    const sfRequestBody = {
      "firstName" : certData.firstName,
      "lastName"  : certData.lastName,
      "streetAddress" : certData.address,
      "city" : certData.city,
      "state" : certData.state,
      "zipCode" : certData.zipCode,
      luckyTruckId: userId
    }

    const sfres = await fetch(sfNewCOIUrl, { method: 'POST', body: JSON.stringify(sfRequestBody), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                .then(res => res.json()) // expecting a json response
    return res.json({
      status: 'ok',
    })
  })

  router.post('/coi', async (req, res, next) => {
    const { name, address, uuid, dotId, policy, userId } = req.body;
    if(!uuid)uuid = await getNewUUID();

    const shellPath = __dirname + '/coi/run_coi.py'
    const path = `/public/coi/coi-${name}${uuid}${moment().format("YYYYMMDDhhmmss")}.pdf`
    let shellCommand = `python ${shellPath} --userId '${userId}' --path '${path}' `
    if (dotId) {
      shellCommand += ` --dotId ${dotId} `
    }
    if (name) {
      shellCommand += `--name "${name}" `
    }
    if (address) {
      shellCommand += `--address '${address}' `
    }
    if (policy) {
      shellCommand += `--policy ${JSON.stringify(policy)} `
    }

    exec(shellCommand, async (error, stdout, stderr) => {
      if (error || stderr) {
        console.log(`error: ${error.message}`);
        return res.json({
          status: 'failure',
          message: 'Failed to upload a new certificate to the Salesforce'
        })
      }

      // upload pdf
      const authSF = await new model.User().getSFToken(userId);
      let accessToken = authSF.access_token;
      let instanceUrl = authSF.instance_url;       
      let sfUploadCOIUrl = `${instanceUrl}/services/apexrest/luckytruck/coi`;

      const pdfContent = await pdf2base64(webConfig.rootDir+path);
      const sfRequestBody = {
        policyId: JSON.parse(policy).policyId,
        pdfContent
      }

      const sfres = await fetch(sfUploadCOIUrl, { method: 'POST', body: JSON.stringify(sfRequestBody), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                  .then(res => res.json()) // expecting a json response
      return res.json({
        status: 'ok',
        pdf: {
          content: pdfContent,
          name: 'COI.pdf'
        }
      })
    });
  })

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
      console.log(result.data.Results);

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
        if(result.data.Results[0].BodyClass)vehiclesTrailers.bodyClass = result.data.Results[0].BodyClass;
      }

      res.send({
        status: "OK",
        data: vehiclesTrailers,
        messages: []
      })
    } catch(e){
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
    let coords = (req.body.coords)?req.body.coords:req.query.coords;
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
    } else{
      so = await companySnapshot.search(keyword).catch(err => console.log(err));
      const state = await getGeoData(coords);
      console.log('state ,', state)
      let filteredData = so;
      if (state) {
        filteredData = so.filter(item => item.location.split(',')[1].trim() == state);
      }
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
    const { usdot, userId } = req.body;
    if ( !usdot ) {
      return res.send({
          status: "ERROR",
          data: {},
          messages: ['usdot is empty']
      })
    }
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
          // let _key = key.replace('address', 'street');
          mailingAddress[key] = tmp[key];
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
        cargoHauled,
        businessStructure
      }

      await new model.Company().create(uuid, '', {}, options );

      res.cookie('uuid', uuid, { maxAge: 9000000, httpOnly: false });
      new model.Company().findByUUID(uuid).then(profile => {
        console.log(profile)
        res.send({
            status: "OK",
            data:{
              company: profile,
              uuid,
            }, //b
            messages: [],
            uuid
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


  router.get('/current', async (req, res, next) => {
    let uuid;
    if(req.query.uuid) uuid = req.query.uuid;
    else if(req.body.uuid) uuid = req.body.uuid;
    else if(req.cookies.uuid) uuid = req.cookies.uuid;
    
    if (uuid) {
      new model.Company().findByUUID(uuid).then(company => {
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
    let authSF = {}
    if (data.signSignature) {
      authSF = await new model.User().getSFToken(data.user_id);
    }

    new model.Company().create(uuid, data.user_id, authSF, data).then(profile => {
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

  // get the polices based upon userId and dotId
  router.post('/accountinfo/policies', async (req, res, next) => {
    const { body: { dotId, userId } } = req;

    const authSF = await new model.User().getSFToken(userId);
    if (authSF.status == 'ok') {
      let accessToken = authSF.access_token;
      let instanceUrl = authSF.instance_url;       
      let sfReadAccountPoliciesUrl = `${instanceUrl}/services/apexrest/account/policy?luckyTruckId=${userId}`;

      let sfCARes = await fetch(sfReadAccountPoliciesUrl, { method: 'GET', headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                    .then(res => res.json()) // expecting a json response
                    .then(json => json);

      console.log(sfCARes)
      if (sfCARes.status == 'Success') {
        res.json({
          status: "ok",
          policies: sfCARes.policies
        })
      } else {
        res.json({
          status: "failure",
          policies: []
        })
      }
    } else {
      res.json({
        status: "failure",
        policies: []
      })
    }
  });

  // get the endorsement list from policy 
  router.post('/accountinfo/policy/endorsements', async (req, res, next) => {
    const { body: { policyId, userId } } = req;

    const authSF = await new model.User().getSFToken(userId);
    if (authSF.status == 'ok') {
      let accessToken = authSF.access_token;
      let instanceUrl = authSF.instance_url;       
      let sfReadAccountPolicyEndorsementUrl = `${instanceUrl}/services/apexrest/account/endorsement?policyId=${policyId}`;

      let sfEndorsementRes = await fetch(sfReadAccountPolicyEndorsementUrl, { method: 'GET', headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                    .then(res => res.json()) // expecting a json response
                    .then(json => json);

      if (sfEndorsementRes.status == 'Success') {
        res.json({
          status: "ok",
          endorsements: sfEndorsementRes.record
        })
      } else {
        res.json({
          status: "failure",
          endorsements: []
        })
      }
    } else {
      res.json({
        status: "failure",
        policies: []
      })
    }
  })

  // get the past certificates from the account
  router.post('/accountinfo/pastcerts', async (req, res, next) => {
    let { body: { userId } } = req;

    const authSF = await new model.User().getSFToken(userId);
    let accessToken = authSF.access_token;
    let instanceUrl = authSF.instance_url;       
    let sfReadAccountPoliciesUrl = `${instanceUrl}/services/apexrest/luckytruck/coi?luckyTruckId=${userId}`;

    let sfCARes = await fetch(sfReadAccountPoliciesUrl, { method: 'GET', headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                  .then(res => res.json()) // expecting a json response

    if (sfCARes.status == 'error') {
      res.json({
        status: "failure",
        certs: [],
      })
    } else {
      res.json({
        status: "ok",
        certs: sfCARes,
      })
    }
  });

  router.post('/accountinfo/quotes', async (req, res, next) => {
    const { body: { dotId, userId } } = req;

    const authSF = await new model.User().getSFToken(userId);
    let accessToken = authSF.access_token;
    let instanceUrl = authSF.instance_url;       
    // let sfReadAccountQuotesUrl = `${instanceUrl}/services/apexrest/luckytruck/insurancequote?luckyTruckId=${userId}`;
    let sfReadAccountQuotesUrl = `${instanceUrl}/services/apexrest/account/quote/?dotId=${dotId}`;

    let sfCARes = await fetch(sfReadAccountQuotesUrl, { method: 'GET', headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                  .then(res => res.json()) // expecting a json response

    if (sfCARes.status == 'Success') {
      res.json({
        status: "ok",
        quoteList: sfCARes.quoteList,
        message: sfCARes.message
      })
    } else {
      res.json({
        status: "failure",
        quoteList: [],
        message: sfCARes.message
      })
    }
  });

  app.use('/api/company', router)
}
