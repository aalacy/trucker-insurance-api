const { Tables } = require("tables");


doIt();

async function doIt(){
  try{
    //db: "mysql://root:1q2w3e4r777y@localhost/simpletest",
    let t = new Tables({
      input: "./2019Mar_Inspection.txt",
      db: "mysql://root:1q2w3e4r5t6y7u8i@localhost/luckytruck",
      batch: 2048,
      guess: 512,
      overwrite: false,
      // If running as a library, you probably want to supress the output
      silent: false
    });

    let result = await t.start();

    console.log(result);
  }catch (e) {
    console.log('got error', e);
    //res.send({'error': e});
  }
}

