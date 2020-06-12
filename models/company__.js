'use strict';
module.exports = (sequelize, DataTypes) => {
  const Company = sequelize.define('Company', {
    imageIdFront: DataTypes.STRING,
    imageIdBack: DataTypes.STRING,
    imageDOT: DataTypes.STRING,
    imageRegistration: DataTypes.STRING
  }, {});
  Company.associate = function(models) {
    // associations can be defined here
  };
  return Company;
};