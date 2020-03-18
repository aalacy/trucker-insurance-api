var webConfig = require("../config/web.js");
const env = process.env.NODE_ENV || 'development';
const config = require(__dirname + '/../config/config.json')[env];
let fs = require('fs');
let ejs = require('ejs');
var HTML5ToPDF = require("html5-to-pdf")

module.exports = {
	getFileName: function(uuid, usdotId, extension=true){
	    return 'coi-'+((usdotId)?usdotId:uuid)+((extension)?'.pdf':'');
  	},
	get: async function(uuid, usdotId, companyModel) {
		
		  
		return new Promise( async (resolve, reject) => {
			try {
				const html5ToPDF = new HTML5ToPDF({
				    inputPath: webConfig.rootDir+'/views/coi/index.html',
				    outputPath: "output.pdf",
				    // templatePath: path.join(__dirname, "templates", "basic"),
				    // include: [
				    //   path.join(__dirname, "assets", "basic.css"),
				    //   path.join(__dirname, "assets", "custom-margin.css"),
				    // ],
				  })
				 
				  await html5ToPDF.start()
				  await html5ToPDF.build()
				  await html5ToPDF.close()
				  console.log("DONE")
				  process.exit(0)
	      	}catch(e){
		        console.log(e);
		        reject(e)
	      	}
		});
	}
}

