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
    key: DataTypes.STRING,
    val: DataTypes.JSON
  }, {});
  Company.associate = function(models) {
    // associations can be defined here
  };

  Company.prototype.findByUUID = async (uuid) => {
    return new Promise((resolve, reject) => {
      Company.findAll({
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
      console.log("USDOT Number",fullProfile);
      if(!fullProfile.businessStructureRaw || !fullProfile.businessStructureRaw["USDOT Number"]){
        reject("USDOT Number not found, can't update Hubspot")
        return
      }

      let properties = [];

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

      if(fullProfile.businessStructureRaw){

        properties.push({"name": "dot_number", "value": fullProfile.businessStructureRaw["USDOT Number"]});
        
        if(fullProfile.businessStructureRaw["DBA Name"])properties.push({"name": "dba_name", "value": fullProfile.businessStructureRaw["DBA Name"]});
        if(fullProfile.businessStructureRaw["Legal Name"])properties.push({"name": "name", "value": fullProfile.businessStructureRaw["Legal Name"]});
        if(fullProfile.businessStructureRaw["Phone"])properties.push({"name": "phone", "value": fullProfile.businessStructureRaw["Phone"]});
        if(fullProfile.businessStructureRaw["Drivers"])properties.push({"name": "total_drivers", "value": fullProfile.businessStructureRaw["Drivers"]});
        if(fullProfile.businessStructureRaw["Power Units"])properties.push({"name": "number_of_power_units", "value": fullProfile.businessStructureRaw["Power Units"]});
        if(fullProfile.businessStructureRaw["MCS-150 Form Date"])properties.push({"name": "mcs150_date", "value": fullProfile.businessStructureRaw["MCS-150 Form Date"]});
        if(fullProfile.businessStructureRaw["MCS-150 Mileage (Year)"])properties.push({"name": "mcs150_mileage_year", "value": fullProfile.businessStructureRaw["MCS-150 Mileage (Year)"]});

        /*
        if(fullProfile.eldProvider["eldProvider"]){
          properties.push({"name": 'eldProvider', "value": fullProfile.eldProvider["eldProvider"].join(', ')});
        }*/

        if(fullProfile.businessStructureRaw["Mailing Address"]){
          let tmp = new Company().parseAndAssignAddress(fullProfile.businessStructureRaw["Mailing Address"], {}, 'mailing_');
          Object.keys(tmp).forEach(function(key) {
            let _key = key.replace('address', 'street');
            properties.push({"name": _key, "value": tmp[key]});
          });
        }

        if(fullProfile.businessStructureRaw["Physical Address"]){
          let tmp = new Company().parseAndAssignAddress(fullProfile.businessStructureRaw["Physical Address"], {}, 'garaging_');
          Object.keys(tmp).forEach(function(key) {
            properties.push({"name": key, "value": tmp[key]});
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
  

  Company.prototype.add = async (uuid, key, val, updateHubspot) => {
    return new Promise(async (resolve, reject) => {
      
      let company = await new Company().findExact(uuid, key);
      if(!company){
        company = new Company();
      }

      company.uuid = uuid;
      company.key = key;
      company.val = val;

      company.save().then(async companyData => {

        if(updateHubspot){
          try{ 
            await new Company().updateHubspot(uuid) 
          }catch(e){
            console.log("Update hubspot catch",e)
          }
        }  
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