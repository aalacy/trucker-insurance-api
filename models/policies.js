'use strict';
module.exports = (sequelize, DataTypes) => {
  const Policies = sequelize.define('Policies', {
    title: DataTypes.STRING,
    type: DataTypes.STRING,
    data: DataTypes.BLOB,
    createdDate: DataTypes.STRING
  }, {});
  Policies.associate = function(models) {
    // associations can be defined here
  };
  return Policies;
};