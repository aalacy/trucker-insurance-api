'use strict';
let randomstring = require("randomstring")
module.exports = (sequelize, DataTypes) => {
    const Token = sequelize.define('Token', {
        userId: DataTypes.INTEGER,
        token: DataTypes.STRING,
        uiScope : DataTypes.JSON
    }, {});
    Token.associate = function (models) {
        // associations can be defined here
        Token.belongsTo(models.User, {
            onDelete: "CASCADE",
            foreignKey: {
                allowNull: false
            }
        });
    };

    Token.prototype.addToken = (user) => {
        return new Promise((resolve, reject) => {
            if (user instanceof sequelize.models.User) {
                Token.create({
                    UserId: user.id, token: randomstring.generate({
                        length: 60,
                        charset: 'alphabetic'
                    })
                }).then(token => {
                    resolve(token);
                    return;
                })
            } else {
                throw "User not instance of models.User"
                reject()
            }
        })

    }

    return Token;
};