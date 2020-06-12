'use strict'

module.exports = (sequelize, DataTypes) => {
    const Certificate = sequelize.define('Certificate', {
        policyId: {
            type: DataTypes.INTEGER,
            allowNull: false
        },
        title: {
            type: DataTypes.STRING,
            allowNull: true,
        },
        type: {
            type: DataTypes.STRING,
            allowNull: true,
        },
        content: {
            type: DataTypes.BLOB,
            allowNull: true,
        },
        data: {
            type: DataTypes.JSON,
            allowNull: true,
        },
    })

    Certificate.associate = function (models) {
        // associations can be defined here
         Certificate.belongsTo(models.User, {
            onDelete: "CASCADE",
            foreignKey: {
                allowNull: false
            }
        });
    }

    Certificate.prototype.create = async (data) => {
        return new Promise((resolve, reject) => {
            let cert = new Certificate()
            cert.setAttributes(data)
            cert.save().then(_case => {
            	resolve('Successfully created.')
            }).catch(err => {
                console.log('========', err);
                reject(err)
                return
            })
        });
    }

    Certificate.prototype.update = async (data, id) => {
        return new Promise((resolve, reject) => {
            Certificate.update(
              data,
              {where: {id} },
            ).catch(err => {
              console.log(err);
              reject(err)
            })
            resolve('Successfully created.')
        });
    }

    Certificate.prototype.findAll = async (UserId) => {
        return new Promise((resolve, reject) => {
          Certificate.findAll({
              where: { UserId },
               order: [
                ['createdAt', 'DESC'],
              ],
            }).then(certs => {
                // certs = certs.map(cert => {
                //     cert.data = cert.data.toString('utf8')
                //     cert.content = new Buffer(cert.content, 'binary').toString('base64')
                //     return cert
                // })
                resolve(certs)
                return
            }).catch(err => {
                reject(err)
            })
        })
      }

    return Certificate;
}