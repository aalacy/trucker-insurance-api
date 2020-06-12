'use strict';
module.exports = (sequelize, DataTypes) => {
  const Cert = sequelize.define('Cert', {
    title: DataTypes.STRING,
    type: DataTypes.STRING,
    data: DataTypes.JSON,
    content: DataTypes.BLOB
  }, {});
  Cert.associate = function(models) {
    // associations can be defined here
     Cert.belongsTo(models.User, {
        onDelete: "CASCADE",
        foreignKey: {
            allowNull: false
        }
    });
  };

  Cert.prototype.create = async (data) => {
    return new Promise((resolve, reject) => {
        let Cert = new Cert()
        cert.setAttributes(data)
        cert.save().then(_cert => {
          resolve('Successfully created.')
        }).catch(err => {
            console.log('========', err);
            reject(err)
            return
        })
    });
  }

  return Cert;
};