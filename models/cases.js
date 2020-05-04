'use strict';
module.exports = (sequelize, DataTypes) => {
  const cases = sequelize.define('cases', {
    subject: DataTypes.STRING
  }, {});
  cases.associate = function(models) {
    // associations can be defined here
  };
  return cases;
};