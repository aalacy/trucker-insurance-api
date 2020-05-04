'use strict'

module.exports = (sequelize, DataTypes) => {
    const Case = sequelize.define('Case', {
        subject: {
            type: DataTypes.STRING,
            allowNull: true,
        },
        message: {
            type: DataTypes.STRING,
            allowNull: true,
        },
        attachments: {
            type: DataTypes.STRING,
            allowNull: true,
        },
    })

    Case.associate = function (models) {
        // associations can be defined here
         Case.belongsTo(models.User, {
            onDelete: "CASCADE",
            foreignKey: {
                allowNull: false
            }
        });
    }

    Case.prototype.submit = async (data) => {

        return new Promise((resolve, reject) => {
            let mycase = new Case()
            mycase.setAttributes(data)
            mycase.save().then(_case => {
            	resolve('Successfully submitted.')
            }).catch(err => {
                console.log('========', err);
                reject(err)
                return
            })
        });
    }

    return Case;
}