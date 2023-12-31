'use strict';
const Hubspot = require('hubspot')
const parseAddress = require('parse-address');
const env = process.env.NODE_ENV || 'development';
const config = require(__dirname + '/../../config/config.json')[env];
const request = require('request');
let User = require("./user");
let pdfApplication = require('../../utils/pdf-application');
var fs = require('fs');
const { exec } = require("child_process");
const hubspot = new Hubspot({ 
  apiKey: config.hapikey,
  checkLimit: false // (Optional) Specify whether or not to check the API limit on each call. Default: true 
});
const fetch = require('node-fetch');

module.exports = (sequelize, DataTypes) => {
  const Company = sequelize.define('Company', {
    uuid: DataTypes.STRING,
    user_id: DataTypes.INTEGER,
    businessStructureRaw: {
      type: DataTypes.BLOB,
      defaultValue: {},
      get() {
        return this.getDataValue('businessStructureRaw') ? this.getDataValue('businessStructureRaw').toString('utf8') : null; 
      },
    },
    name: DataTypes.STRING,
    dotNumber: DataTypes.STRING,
    dotNumber: DataTypes.STRING,
    dba: DataTypes.STRING,
    powerUnits: DataTypes.STRING,
    phoneNumber: DataTypes.STRING,
    mailingAddress: {
      type: DataTypes.BLOB,
      defaultValue: {},
      get() {
        return this.getDataValue('mailingAddress')? this.getDataValue('mailingAddress').toString('utf8') : null; 
      },
    },
    garagingAddress: {
      type: DataTypes.BLOB,
      defaultValue: {},
      get() {
        return this.getDataValue('mailingAddress') ? this.getDataValue('garagingAddress').toString('utf8') : null; 
      },
    },
    emailAddress: DataTypes.STRING,
    mcNumber: DataTypes.STRING,
    travelRadius: DataTypes.STRING,
    currentCarrier: {
      type: DataTypes.BLOB,
      defaultValue: [],
      get() {
        return this.getDataValue('currentCarrier') ? this.getDataValue('currentCarrier').toString('utf8') : null; 
      },
    },
    currentEldProvider: {
      type: DataTypes.BLOB,
      defaultValue: [],
      get() {
        return this.getDataValue('currentEldProvider') ? this.getDataValue('currentEldProvider').toString('utf8') : null; 
      },
    },
    cargoHauled: {
      type: DataTypes.BLOB,
      defaultValue: {},
      get() {
        return this.getDataValue('cargoHauled') ? this.getDataValue('cargoHauled').toString('utf8') : null; 
      },
    },
    cargoGroup: {
      type: DataTypes.BLOB,
      defaultValue: [],
      get() {
        return this.getDataValue('cargoGroup') ? this.getDataValue('cargoGroup').toString('utf8') : null; 
      },
    },
    ownerName: DataTypes.STRING,
    businessStructure: DataTypes.STRING,
    businessType: DataTypes.STRING,
    driverInformationList: {
      type: DataTypes.BLOB,
      defaultValue: [],
      get() {
        return this.getDataValue('driverInformationList') ? this.getDataValue('driverInformationList').toString('utf8') : null; 
      },
    },
    ownerInformationList: {
      type: DataTypes.BLOB,
      defaultValue: [],
      get() {
        return this.getDataValue('ownerInformationList') ? this.getDataValue('ownerInformationList').toString('utf8') : null; 
      },
    },
    vehicleInformationList: {
      type: DataTypes.BLOB,
      defaultValue: [],
      get() {
        return this.getDataValue('vehicleInformationList') ? this.getDataValue('vehicleInformationList').toString('utf8') : null; 
      },
    },
    comments: DataTypes.TEXT,
    attachmentList: {
      type: DataTypes.BLOB,
      defaultValue: [],
      get() {
        return this.getDataValue('attachmentList') ? this.getDataValue('attachmentList').toString('utf8') : null; 
      },
    },
    signSignature: {
      type: DataTypes.BLOB,
      get() {
        return this.getDataValue('signSignature') ? this.getDataValue('signSignature').toString('utf8') : null; 
      },
    },
    nico_questions: {
      type: DataTypes.BLOB,
      defaultValue: {},
      get() {
        return this.getDataValue('nico_questions') ? this.getDataValue('nico_questions').toString('utf8') : null; 
      },
    },
    imageIdFront: {
      type: DataTypes.BLOB,
      get() {
        return this.getDataValue('imageIdFront') ? this.getDataValue('imageIdFront').toString('utf8') : null; 
      },
    },
    imageIdBack: {
      type: DataTypes.BLOB,
      get() {
        return this.getDataValue('imageIdBack') ? this.getDataValue('imageIdBack').toString('utf8') : null; 
      },
    },
    imageDOT: {
      type: DataTypes.BLOB,
      get() {
        return this.getDataValue('imageDOT') ? this.getDataValue('imageDOT').toString('utf8') : null; 
      },
    },
    imageRegistration: {
      type: DataTypes.BLOB,
      get() {
        return this.getDataValue('imageRegistration') ? this.getDataValue('imageRegistration').toString('utf8') : null; 
      },
    },
    sf_status: DataTypes.STRING,
    is_quote_modified: DataTypes.BOOLEAN,
    is_coi_modified: DataTypes.BOOLEAN,
  }, {});
  Company.associate = function(models) {
    // associations can be defined here
  };

  Company.prototype.findByUserId = async (user_id) => {
    return new Promise((resolve, reject) => {
      Company.findAll({
          where: { user_id },
           order: [
            ['createdAt', 'DESC'],
          ],
        }).then(companies => {
            resolve(companies)
            return
        }).catch(err => {
            reject(err)
        })
    })
  }

  Company.prototype.findByUUID = async (uuid) => {
    return new Promise((resolve, reject) => {
      Company.findOne({
            where: {"uuid" : uuid},
        }).then(company => {
            resolve(company)
            return
        }).catch(err => {
            reject(err)
        })
    })
  }

  Company.prototype.findExact = async (uuid, key) => {
    return new Promise((resolve, reject) => {
      Company.findOne({
            where: {"uuid" : uuid, "key" : key},
        }).then(company => {
            resolve(company)
            return
        }).catch(err => {
            reject(err)
        })
    })
  }

  // validate and format if the value is null
  const _v = (value) => {
    if (value == undefined) {
      return null;
    } else if (value && value.length == 0) {
      return null;
    } else {
      return value;
    }
  }

  const _a = (arr) => {
    if (arr == undefined) {
      return []; 
    } else {
      return arr;
    }
  }

  const parseJsonFromObject = (obj) => {
    if (obj.constructor !== Object) {
      try {
        return JSON.parse(obj);
      } catch (e) {}
    } else {
      return obj;
    }
  }

  const parseJsonFromArray = (arr) => {
    if (!Array.isArray(arr)) {
      try {
        return JSON.parse(arr);
      } catch (e) {}
    } else {
      return arr;
    }
  }

  const formatKeysOfCargoHauled = (obj) => {
    return {
      "misc" : _a(obj["Misc."]),
      "buildingSupplies":  _a(obj["Building Supplies"]),
      "machineryEquipment" :  _a(obj["Machinery / Equipment"]),
      "autos" :  _a(obj["Autos / Aircrafts / Boats"]),
      "consumerGoods":  _a(obj["Consumer Goods"]),
      "paper" :  _a(obj["Paper / Plastic / Glass"]),
      "construction" :  _a(obj["Construction Materials (Raw)"]),
      "metals" :  _a(obj["Metals / Coal"]),
      "chemicals" :  _a(obj["Chemicals"]),
      "farming" :  _a(obj["Farming / Agriculture / Livestock"]),
      "textiles" :  _a(obj["Textiles / Skins / Furs"]),
      "food" :  _a(obj["Food & Beverages"])
    }
  }

  const formatOwnerInfoList = (arr) => {
    const newList = [];
    arr.map(owner => {
      newList.push({
        firstName: owner.firstName,
        LastName: owner.lastName,
        dob: `${owner.dobY}-${owner.dobM}-${owner.dobD}`,
        address: {
          street: owner.address,
          city: owner.city,
          state: owner.state,
          zip: owner.zip
        }
      })
    })
    return newList;
  }

  const formatDriverInfoList = (arr) => {
    const newList = [];
    arr.map(driver => {
      newList.push({
        firstName: driver.firstName,
        LastName: driver.lastName,
        dob: `${driver.dobY}-${driver.dobM}-${driver.dobD}`,
        state: driver.state,
        licenseNumber: driver.licenseNumber,
        hireDate: `${driver.dohY}-${driver.dohM}-${driver.dohD}`,
        cdl: _v(driver.CDL),
        yearsOfExperience: null
      });
    });
    return newList;
  }

  const formatVehicleInformationList = (arr) => {
    let newList = [];
    if(arr.vehicle.length){
       arr.vehicle.map((vehicle, i) => {
          newList.push({
            "name" : vehicle.model,
            "vin" : vehicle.VIN, 
            "year" : vehicle.year,
            "make" : vehicle.make,
            "vehicleType" : vehicle.vehicleType, 
            "travelRadius": vehicle.radiusOfTravelVehicle,
            "garageZipCode" : vehicle.zipCode,
            "collisionCoverage" : _v(vehicle.coverage),
            "vehicleValue" : _v(vehicle.currentValue),
            "deductible" : _v(vehicle.deductible)
          })
       })
    }

    if(arr.trailer.length){
       arr.trailer.map((vehicle, i) => {
          newList.push({
            "name" : vehicle.model,
            "vin" : vehicle.VIN, 
            "year" : vehicle.year,
            "make" : vehicle.make,
            "vehicleType" : vehicle.trailerType, 
            "travelRadius": vehicle.radiusOfTravelTrailer,
            "garageZipCode" : vehicle.zipCode,
            "collisionCoverage" : _v(vehicle.coverage),
            "vehicleValue" : _v(vehicle.currentValue),
            "deductible" : _v(vehicle.deductible)
          })
       })
    }

    return newList;
  }

  const formatAddress = obj => {
    return {
      street: obj.address,
      zip: obj.zip,
      city: obj.city,
      state: obj.state
    };
  }  

  Company.prototype.updateSalesforce = async (uuid, userId, authSF, nicoPdf, oldPdf) => {
    let accessToken = authSF.access_token;
    let instanceUrl = authSF.instance_url;       
    let sfCAUrl = `${instanceUrl}/services/apexrest/applications`;

    if (!accessToken) {
      return "Something wrong happened in the server. please try again later, or contact the customer service if you see this error message again";
    }

    let profile = await new Company().findByUUID(uuid);

    let attachmentList = parseJsonFromArray(profile.attachmentList);
    let imageSign = parseJsonFromObject(profile.signSignature).imageSign;
    let newAttachmentList = [];
    attachmentList.forEach(function(attachment) {
      if (attachment.name && attachment.name.length) {
        newAttachmentList.push(attachment);
      }
    });

    // signature image
    newAttachmentList.push({
      name: "signature.jpeg",
      content: _v(imageSign)
    })

    // Old application pdf 
    newAttachmentList.push({
      name: `Application for ${profile.name}.pdf`,
      content: _v(oldPdf)
    })

    // Nico app pdf
    newAttachmentList.push({
      name: `Application for ${profile.name} - NICO.pdf`,
      content: _v(nicoPdf)
    })

    let sfRequestBody = {
      luckyTruckId: userId,
      "accountWrapper": {
        "name": profile.name,
        "dotNumber": profile.dotNumber,
        "dba": profile.dba,
        "phoneNumber": profile.phoneNumber,
        "mailingAddress": formatAddress(parseJsonFromObject(profile.mailingAddress)),
        "garagingAddress": formatAddress(parseJsonFromObject(profile.garagingAddress)),
        "emailAddress": profile.emailAddress,
        "mcNumber": profile.mcNumber,
        "currentCarrier": parseJsonFromArray(profile.currentCarrier),
        "currentEldProvider": parseJsonFromArray(profile.currentEldProvider),
        "cargoGroup": parseJsonFromArray(profile.cargoGroup),
        "cargoHauled": formatKeysOfCargoHauled(parseJsonFromObject(profile.cargoHauled)),
        "businessStructure" : _v(profile.businessStructure),
        "businessType" : _v(profile.businessType)
      },
      "ownerInformation": formatOwnerInfoList(parseJsonFromArray(profile.ownerInformationList)),
      "driverInformationList": formatDriverInfoList(parseJsonFromArray(profile.driverInformationList)),
      "vehicleInformationList": formatVehicleInformationList(parseJsonFromObject(profile.vehicleInformationList)),
      "comments": _v(profile.comments),
      "attachmentList": newAttachmentList,
      nico_questions: profile.nico_questions
    };
    fetch(sfCAUrl, { method: 'POST', body: JSON.stringify(sfRequestBody), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                  .then(res => res.json()) // expecting a json response
                  .then(json => {
                    Company.update(
                      {
                        sf_status: 'ok'
                      },
                      {where: {uuid} },
                    ).catch(err => {
                      console.log(err);
                    })
                    sequelize.models.User.update({ 
                      dotId: profile.dotNumber,
                      account_status: 'submitted'
                    }, { where: { id: userId }}).catch(err => {
                      console.log(err);
                    })
                  })
                  .catch(err => {
                    console.log(err)
                    Company.update(
                      {
                        sf_status: JSON.stringify(err)
                      },
                      {where: {uuid} },
                    ).catch(err => {
                      console.log(err);
                    })
                  })
  }

  Company.prototype.updateHubspot = async (uuid, key, val) => {
    console.log('profile update hubspot:');
    return new Promise(async (resolve, reject) => {
        
      let profile = await new Company().findByUUID(uuid);
      if(!profile){
        console.log('profile false updatehubspot:',!profile);
        reject('the company not found by uuid')
        return
      }

      let fullProfile = new Company().renderAllByType(profile);
      let businessStructureRaw = {};
      try {
       businessStructureRaw = JSON.parse(fullProfile.businessStructureRaw);
      } catch (e) {
        console.log(e)
      }
      if(!fullProfile.businessStructureRaw || !businessStructureRaw["USDOT Number"]){
        reject("USDOT Number not found, can't update Salesforce")
        return
      }

      let properties = [];
      let accountWrapper = {}

      /* add fields to update */

      if(fullProfile.personalInfo){
        if(fullProfile.personalInfo["firstName"] || fullProfile.personalInfo["lastName"]){
          let flname = fullProfile.personalInfo["firstName"] + " "+fullProfile.personalInfo["lastName"];
          properties.push({"name": "full_name", "value": flname.trim()});
        }

        if(fullProfile.personalInfo["city"])properties.push({"name": "city", "value": fullProfile.personalInfo["city"]});
        if(fullProfile.personalInfo["state"])properties.push({"name": "state", "value": fullProfile.personalInfo["state"]});
        if(fullProfile.personalInfo["zip"])properties.push({"name": "zip", "value": fullProfile.personalInfo["zip"]});
        if(fullProfile.personalInfo["address"])properties.push({"name": "address", "value": fullProfile.personalInfo["address"]});
      }

      if(businessStructureRaw){
        accountWrapper.name = businessStructureRaw['Legal Name'];
        accountWrapper.dotNumber = businessStructureRaw['USDOT Number'];
        accountWrapper.dba = businessStructureRaw['DBA Name'];
        accountWrapper.phoneNumber = businessStructureRaw['Phone'];
        accountWrapper.mailingAddress = {};
        accountWrapper.garagingAddress = {};
        accountWrapper.emailAddress = "";
        accountWrapper.mcNumber = businessStructureRaw['MC/MX/FF Number(s)'];
        accountWrapper.travelRadius = "";
        accountWrapper.currentCarrier = JSON.stringify(businessStructureRaw['Carrier Operation']);
        accountWrapper.currentEldProvider = "";
        accountWrapper.cargoHauled = "";


        if(businessStructureRaw["Mailing Address"]){
          let tmp = new Company().parseAndAssignAddress(businessStructureRaw["Mailing Address"], {}, '');
          Object.keys(tmp).forEach(function(key) {
            let _key = key.replace('address', 'street');
            accountWrapper.mailingAddress[_key] = tmp[key];
          });
        }

        if(businessStructureRaw["Physical Address"]){
          let tmp = new Company().parseAndAssignAddress(businessStructureRaw["Physical Address"], {}, '');
          Object.keys(tmp).forEach(function(key) {
            accountWrapper.garagingAddress[key] = tmp[key];
          });
        }
      }

      /* end fields to update */

/*
      resolve(properties);
      return;*/

      const companyObj = {
        "properties": properties
      };

      //fullProfile.businessStructureRaw["USDOT Number"] = 'uuuuuuu';

      // let hubspotCompany = await hubspot.companies.getByDomain().catch(err => {
        // console.log("hubspot Company err",err)
        //reject(err)
        //return
      // })
      const companyRequestBody = {
        "limit": 2,
        "requestOptions": {
        "properties": [
            "domain",
            "createdate",
            "name",
            "hs_lastmodifieddate"
          ]
        },
        "offset": {
          "isPrimary": true,
          "companyId": 0
        }
      }
      let hubspotCompany = await fetch(`https://api.hubapi.com/companies/v2/domains/1306514.dot/companies?hapikey=${config.hapikey}`, { method: 'POST', body: JSON.stringify(companyRequestBody), headers: {'Content-Type': 'application/json'} })
                                  .then(res => res.json()) // expecting a json response
                                  .then(json => json);

      let resp;
      if(!hubspotCompany || hubspotCompany.results.length === 0 || !hubspotCompany.results[0].companyId){
        console.log("hubspotCompany",hubspotCompany);
        console.log("hubspotCompany[0].companyId",hubspotCompany[0].companyId);
        //resolve(hubspotCompany);
        //reject('create new not yet implemented')
        properties.push({"name": "domain", "value": fullProfile.businessStructureRaw["USDOT Number"]+'.dot'});
        resp = await hubspot.companies.create(companyObj);
        console.log('create!',resp);
      }else{
        try{resp = await hubspot.companies.update(hubspotCompany.results[0].companyId, companyObj);
          console.log("resp update",resp);
          console.log('update!');
        }
        catch (err) { 
          console.log("update err",err)}
        console.log("resp update",resp);
        console.log('update!');
      }

      await pdfApplication.uploadToHubspot(uuid, resp.companyId, await new Company()).catch(err => {
        console.log('hubspotError',err)
      })

      request.get('https://api.hubapi.com/crm-associations/v1/associations/'+resp.companyId+'/HUBSPOT_DEFINED/6?hapikey='+config.hapikey, async (error, res, body) => {
        if (!error) {
          //console.log(`statusCode: ${res.statusCode}`)
          //console.log(body)
          let obj = JSON.parse(body);
          if(obj && Array.isArray(obj.results) && obj.results.length == 0){
            let dealsProp = [];
            dealsProp.push({"name": 'dealname', "value": 'auto company deal'});
            dealsProp.push({"name": 'description', "value": 'no description'});
            dealsProp.push({"name": 'full_name', "value": ''});
            dealsProp.push({"name": 'phone_number', "value": ''});
            dealsProp.push({"name": 'email_address', "value": ''});
            const dealsObj = {
              "associations": {
                "associatedCompanyIds": [
                  resp.companyId
                ]
              },
              "properties": dealsProp
            };
            
            console.log('deals', dealsObj);
            let dealLog = await hubspot.deals.create(dealsObj);
           console.log(dealLog);
          }

        }else{
          console.error(error)
        }
      
      })
        console.log('hubspotrespone:'+ JSON.stringify(resp));
      resolve(resp);
    
    })
  }

  Company.prototype.create = async (uuid, userId, authSF, options) =>{
    return new Promise(async (resolve, reject) => {
      let company = await new Company().findByUUID(uuid);
      if(!company){ // create new company record
        company = new Company();
        company.uuid = uuid;
        Object.keys(options).forEach(function(key) {
          company[key] = options[key];
        });
        const companyData = await company.save()
                                        .catch(err => {
                                          reject(err);
                                        });
        resolve('Ok');
      } else { // update company based on UUID
        await Company.update(
           options,
           {where: {uuid} },
        ).catch(err => {
          reject(err);
        })

        if (options.signSignature) {
            // generate nico pdf
            const shellPython = config.python + ' ' + __dirname + '/../../routes/coi/run_nico.py'
            let shellCommand = `${shellPython} --uuid ${uuid}`

            const pdfPath = __dirname + `/../../public/nico/nico-${uuid}.pdf`

            exec(shellCommand, async (error, stdout, stderr) => {
              if (error || stderr) {
                console.log(error, stderr)
              }

              fs.readFile(pdfPath, function (err, nicoPdf){
                // Read old app pdf
                pdfApplication.get(uuid, 0, new Company()).then(location => {
                  fs.readFile(location, function (err, oldPdf){
                      new Company().updateSalesforce(uuid, userId, authSF, nicoPdf, oldPdf);
                    });
                  })
               });
            })
        }
        resolve('Ok');
      }
    });
  }

  Company.prototype.add = async (uuid, key, val, updateHubspot) => {
    return new Promise(async (resolve, reject) => {
      
      let company = await new Company().findByUUID(uuid);
      if(!company){
        company = new Company();
      }

      company.uuid = uuid;
      company.key = key;
      company.val = val;

      company.save().then(async companyData => {
        resolve(companyData);
      }).catch(err => {
        console.log("update hubspot error",err)
          reject(err)
          return
      })

    })
  }

  Company.prototype.parseAndAssignAddress = (source, obj, prefix) => {
    let parsed, address;
    parsed = parseAddress.parseLocation(source);
    address = [];

    if(parsed.number)address.push(parsed.number); 
    if(parsed.prefix)address.push(parsed.prefix); 
    if(parsed.street)address.push(parsed.street); 

    if(address.length)obj[prefix+'address'] = address.join(' ');
    if(parsed.city)obj[prefix+'city'] = parsed.city;
    if(parsed.zip)obj[prefix+'zip'] = parsed.zip;
    if(parsed.state)obj[prefix+'state'] = parsed.state;
    return obj;
  }

  Company.prototype.renderOne = (company) => {
    company = company.dataValues
    return company
  }

  Company.prototype.renderAll = (companies) => {

    let list = [];
    companies.forEach(function(company) {
      //console.log(company,'******');
      list.push(new Company().renderOne(company))
    });

    return list
  }

  Company.prototype.renderAllByType = (companies) => {

    let list = {};
    companies.forEach(function(company) {
      //console.log(company,'******');
      list[company.key] = company.val;
    });

    return list
  }

  Company.prototype.update = async (uuid, options) => {
    return new Promise(async (resolve, reject) => {
      let company = await new Company().findByUUID(uuid);
      if (company) {
        await Company.update(
           options,
           {where: {uuid} },
        ).catch(err => {
          reject(err);
        })
        resolve('ok')
      } else {
        reject('company not found')
      }
    });
  }

  return Company;
};