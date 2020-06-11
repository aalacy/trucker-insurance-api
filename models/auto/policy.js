'use strict'

module.exports = (sequelize, DataTypes) => {
    const Policy = sequelize.define('Policy', {
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

    Policy.associate = function (models) {
        // associations can be defined here
         Policy.belongsTo(models.User, {
            onDelete: "CASCADE",
            foreignKey: {
                allowNull: false
            }
        });
    }

    Policy.prototype.create = async (data) => {
        return new Promise((resolve, reject) => {
            let policy = new Policy()
            policy.setAttributes(data)
            policy.save().then(_case => {
            	resolve('Successfully submitted.')
            }).catch(err => {
                console.log('========', err);
                reject(err)
                return
            })
        });
    }

    return Policy;
}