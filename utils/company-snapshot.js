const cheerio = require('cheerio');
const tabletojson = require('tabletojson');
let fs = require('fs');
let request = require("request");

module.exports = {
  get: async function(usdot) {
    return new Promise((resolve, reject) => {
      //console.log("https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string="+usdot);
      let _this = this;
      request({ 
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
        },
        uri: "https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string="+usdot },
        function(error, response, body) {
            if(error){
              reject("Got error: " + error);
              return;
            }
            if(!body){
              reject("empty response from the server");
              return;
            }
            resolve(_this.parseHTML(body));
        }
      );

    })
  },
  search: async function(name) {
    return new Promise((resolve, reject) => {
      //console.log("https://safer.fmcsa.dot.gov/keywordx.asp?searchstring=%2A"+encodeURIComponent(name)+"%2A");
      let _this = this;
      request(
          { 
            headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
          },
          uri: "https://safer.fmcsa.dot.gov/keywordx.asp?searchstring=%2A"+encodeURIComponent(name)+"%2A" },
          function(error, response, body) {
              if(error){
                reject("Got error: " + error);
                return;
              }
              if(!body){
                reject("empty response from the server");
                return;
              }
              // console.log('Body:'+ JSON.parse(response));
              resolve(_this.findCandidates(body));
          }
      );

    })
  },
  test: function() {

    let html = fs.readFileSync('./tmp/_tmp/test2a.html', 'utf8');
    return this.parseHTML(html);
    //let html = fs.readFileSync('./tmp/_tmp/test.html', 'utf8');
    //return this.findCandidates(html);
  },
  findCandidates: function(html) {
      const $ = cheerio.load(html);
      let ret = [];
      
      $("th[scope=rpw]").map(function (i, element){
          if($(element).find('a:nth-of-type(1)').text().trim() === '')return;
          var usdot = $(element).find('a:nth-of-type(1)').attr('href');
              usdot = usdot.match(/query_string=([^&]+)/)
              if(usdot[1])usdot = usdot[1];
          ret.push({
            name: $(element).find('a:nth-of-type(1)').text().trim(),
            location: $(element).next('td').text().trim(),
            usdot: usdot
          });
      }).get()

      return ret;
  },
  parseHTML: function(html) {
      const $ = cheerio.load(html);
      let ret = {};

      $("th").map(function (i, element){
          if($(element).find('a:nth-of-type(1)').text().trim() === '')return;
          ret[$(element).find('a:nth-of-type(1)').text().replace(':', '').trim()] = $(element).next('td').text().trim();
      }).get()
      
      let tmp = ["Operation Classification", "Carrier Operation", "Cargo Carried"];
      tmp.forEach(colspan4 => {
        
          let so = $("table[summary='"+colspan4+"'] font").map(function (i, element){
              if($(element).text().trim() === '')return;
              //console.log('*****'+$(element).parent().parent().find("td[class='queryfield']").text().trim()+'******');
              if($(element).parent().parent().find("td[class='queryfield']").text().trim() !== 'X'){
                return;
              }
              return $(element).text().trim();
          }).get()

          $("table[summary='"+colspan4+"'] td[class='queryfield']").map(function (i, element){
              if($(element).text().trim() !== 'TOOLS')return;
              if(!ret[colspan4])ret[colspan4] = [];
              ret[colspan4].push('please specify');
          }).get()

          if(so.length)ret[colspan4] = so;
        });

      let countries = ['US', 'Canada'];
      tmp = ["Inspections", "Crashes"];
      tmp.forEach(subtable => {
          $("table[summary='"+subtable+"']").map(function (i, element){

              const converted = tabletojson.convert(cheerio.html(element), { useFirstRowForHeadings: true });

              /* v1 */
              let tmp_array = {};
              for(var k in converted[0]){
                  if(parseInt(k) === 0)continue;
                  let _tmp_field_name = Object.keys(converted[0][k])[0];
                  let _key = converted[0][k][_tmp_field_name];
                  delete converted[0][k][_tmp_field_name];
                  tmp_array[_key] = converted[0][k];
              }
              /* ** */

              /* v2 */
              //tmp_array = converted;
              /* ** */

              if(!tmp_array)return;

              if(!ret[subtable])ret[subtable] = {};
              ret[subtable][countries[i]] = tmp_array;

          }).get()
        });


        $("table[summary='Review Information'] th").map(function (i, element){
          if($(element).text().trim() === '' || $(element).text().trim() === 'Review Information')return;
          if(!ret['Review Information'])ret['Review Information'] = {};
          ret['Review Information'][$(element).text().trim()] = $(element).next('td').text().trim();
      }).get()

      return ret;
  }
};