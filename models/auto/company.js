'use strict';
const Hubspot = require('hubspot')
const parseAddress = require('parse-address');
const env = process.env.NODE_ENV || 'development';
const config = require(__dirname + '/../../config/config.json')[env];
const request = require('request');
let pdfApplication = require('../../utils/pdf-application');
const hubspot = new Hubspot({ 
  apiKey: config.hapikey,
  checkLimit: false // (Optional) Specify whether or not to check the API limit on each call. Default: true 
});
const fetch = require('node-fetch');

module.exports = (sequelize, DataTypes) => {
  const Company = sequelize.define('Company', {
    uuid: DataTypes.STRING,
    businessStructureRaw: DataTypes.JSON,
    name: DataTypes.STRING,
    dotNumber: DataTypes.STRING,
    dotNumber: DataTypes.STRING,
    dba: DataTypes.STRING,
    powerUnits: DataTypes.STRING,
    phoneNumber: DataTypes.STRING,
    mailingAddress: DataTypes.JSON,
    garagingAddress: DataTypes.JSON,
    emailAddress: DataTypes.STRING,
    mcNumber: DataTypes.STRING,
    travelRadius: DataTypes.STRING,
    currentCarrier: DataTypes.JSON,
    currentEldProvider: DataTypes.JSON,
    cargoHauled: DataTypes.JSON,
    cargoGroup: DataTypes.JSON,
    ownerName: DataTypes.STRING,
    businessStructure: DataTypes.STRING,
    businessType: DataTypes.STRING,
    driverInformationList: DataTypes.JSON,
    ownerInformationList: DataTypes.JSON,
    vehicleInformationList: DataTypes.JSON,
    comments: DataTypes.TEXT,
    attachmentList: DataTypes.JSON,
    signSignature: DataTypes.JSON,
    imageIdFront: DataTypes.JSON,
    imageIdBack: DataTypes.JSON,
    imageDOT: DataTypes.JSON,
    imageRegistration: DataTypes.JSON,
  }, {});
  Company.associate = function(models) {
    // associations can be defined here
  };

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

  const authSalesforce = async () => {
    return await fetch(`https://${config.sf_server}.salesforce.com/services/oauth2/token?grant_type=password&client_id=${config.sf_client_id}&client_secret=${config.sf_client_secret}&username=${config.sf_username}&password=${config.sf_password}`, { method: 'POST', headers: {'Content-Type': 'application/json'} })
                  .then(res => res.json()) // expecting a json response
                  .then(json => json);
  }

  Company.prototype.updateSalesforce = async(uuid) => {
    console.log('profile update salesforce:');
    
    const sfATRes = await authSalesforce();
    let accessToken = sfATRes.access_token;
    let instanceUrl = sfATRes.instance_url;       
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
    newAttachmentList.push({
      name: "signature.jpeg",
      content: _v(imageSign)
    })

    let sfRequestBody = {
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
      "attachmentList": newAttachmentList
    };
    let sfCARes = await fetch(sfCAUrl, { method: 'POST', body: JSON.stringify(sfRequestBody), headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + accessToken} })
                  .then(res => res.json()) // expecting a json response
                  .then(json => json);

    console.log("create app in salesforce: ", sfCARes);
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

  Company.prototype.create = async (uuid, options) =>{
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
          const res = new Company().updateSalesforce(uuid);
          if (res) {
            reject(res);
          }
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

  return Company;
};