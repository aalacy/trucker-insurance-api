'use strict'
let md5 = require('md5')
let fs = require('fs')
let stringHelper = require('../../helpers/string')
let im = require('imagemagick');
let webConfig = require('../../config/web.js')
let sanitize = require("sanitize-filename");
const uuid = require('uuid/v4');
const moment = require('moment');
const fetch = require('node-fetch');
const env = process.env.NODE_ENV || 'development';
const config = require(__dirname + '/../../config/config.json')[env];

const authSalesforce = async () => {
    return await fetch(`https://${config.sf_server}.salesforce.com/services/oauth2/token?grant_type=password&client_id=${config.sf_client_id}&client_secret=${config.sf_client_secret}&username=${config.sf_username}&password=${config.sf_password}`, { method: 'POST', headers: {'Content-Type': 'application/json'} })
        .then(res => res.json()) // expecting a json response
        .then(json => json);
}

module.exports = (sequelize, DataTypes) => {
    const User = sequelize.define('User', {
        firstName: {
            type: DataTypes.STRING,
            allowNull: true,
        },
        lastName: {
            type: DataTypes.STRING,
            allowNull: true,
        },
        email: {
            type: DataTypes.STRING,
            validate: {
                isEmail: {
                    msg: "Invalid email address"
                },
                scenario : function() {
                    switch (this._modelOptions.scenario) {
                        case 'create'   :
                            if (!this.email || this.email.length == 0) {
                                throw new Error('Email required')
                            }
                            break
                    }
                },
                isUnique : function() {
                    if (this.isNewRecord) {
                        return User.findOne({where : {email : this.email}}).then(user => {
                            // console.log(user)
                            if (user != null) {
                                throw new Error('Email address in use')
                            }
                        }).catch(err => {
                            throw new Error(err)
                        })
                    }
                }
            },
            allowNull: true,
        },
        password: {
            type: DataTypes.STRING,
            allowNull: true,
            validate: {
                scenario : function() {
                    switch (this._modelOptions.scenario) {
                        case 'create'   :
                            if (!this.password || this.password.length == 0) {
                                throw new Error('Password required')
                            }
                            if (!this._modelOptions.passwordConfirm || this._modelOptions.passwordConfirm.length == 0) {
                                throw new Error('Confirm password required')
                            }

                            if (this.password != this._modelOptions.passwordConfirm) {
                                throw new Error('Passwords not match')
                            }
                            this.password = md5(this.password)
                            break

                        case 'update' :
                            if ((this.facebookId == null && this.twitterId == null) || this._previousDataValues.password != null) {
                                if (this._modelOptions.oldPassword != null) {

                                    if (md5(this._modelOptions.oldPassword) != this._previousDataValues.password) {
                                        throw new Error('Invalid old password')
                                    }


                                    if (this._modelOptions.passwordConfirm == null ||this._modelOptions.passwordConfirm.length == 0) {
                                        throw new Error('Password confirm can not be blank')
                                    }

                                    if (this.password.length == 0) {
                                        throw new Error('New password can not be blank')
                                    }


                                    if (this._modelOptions.passwordConfirm != this.password) {
                                        throw new Error('Password confirmation not match')
                                    }
                                    this.password = md5(this.password)
                                } else {
                                    this.password = this._previousDataValues.password
                                }
                            } else {
                                if (this._modelOptions.passwordConfirm == null ||this._modelOptions.passwordConfirm.length == 0) {
                                    throw new Error('Password confirm can not be blank')
                                }

                                if (this.password.length == 0) {
                                    throw new Error('New password can not be blank')
                                }


                                if (this._modelOptions.passwordConfirm != this.password) {
                                    throw new Error('Password confirmation not match')
                                }
                                this.password = md5(this.password)
                            }
                            break

                            case 'reset-password' :

                                if (this._modelOptions.passwordConfirm == null ||this._modelOptions.passwordConfirm.length == 0) {
                                    throw new Error('Password confirm can not be blank')
                                }

                                if (this.password.length == 0) {
                                    throw new Error('New password can not be blank')
                                }


                                if (this._modelOptions.passwordConfirm != this.password) {
                                    throw new Error('Password confirmation not match')
                                }
                                this.password = md5(this.password)
                            
                            break
                    }
                }
            }
        },
        facebookId: {
            type: DataTypes.INTEGER,
            allowNull: true,
            validate: {}
        },
        twitterId: {
            type: DataTypes.INTEGER,
            allowNull: true,
            validate: {}
        },
        googleId: {
            type: DataTypes.INTEGER,
            allowNull: true,
            validate: {}
        },
        admin: DataTypes.INTEGER,
        social: DataTypes.INTEGER,
        dotId: DataTypes.INTEGER,
        role:DataTypes.STRING,
        companyName:DataTypes.STRING,
        sf_token:DataTypes.STRING,
        sf_instance_url:DataTypes.STRING,
        sf_token_expired:DataTypes.DATE,
        account_status:DataTypes.STRING,
    }, {
        passwordConfirm: null,
        oldPassword: null,
        scenario: null
    })
    User.associate = function (models) {
        // associations can be defined here
        User.hasMany(models.Token);
        User.hasOne(models.UserData);
    }
    
    User.prototype.getProfileImageLocation = (profileImage) => {

        profileImage = sanitize(profileImage);
        if(!profileImage)return '';
        return webConfig.rootDir +"/uploads/profile-images/"+profileImage;

    }

    User.prototype.getProfileImageUrl = (profileImage) => {

        let data = {
            raw: '', 
            thumb: ''
        }

        if(profileImage){
            data.raw = webConfig.rootDomain+"/api/1/user/download-profile-image?fn="+profileImage;
            data.thumb = webConfig.rootDomain+"/api/1/user/download-profile-image?fn="+profileImage+"_98x98.jpg";
        }
            
        return data;

    }

    User.prototype.updateProfileImage = async (user, files) => {
        return new Promise((resolve, reject) => {

            try{
            
                if(files.length){

                    let physical_docs = [];
                    for(let c = 0; c < 1; c++){//files.length

                        let _file = files[c];
                        //console.log("a file detected! >>>>"+_file['originalname']);

                        if(_file['fieldname'] !== 'profileImage[]')continue;
                        //console.log("fieldname is good! >>>>"+_file['originalname']);
                        im.resize({
                            srcPath: _file['path'],
                            dstPath: _file['path']+'_98x98.jpg',
                            width:   98,
                            height:   98,
                          }, function(err, stdout, stderr){
                            if (err){
                                fs.unlink(_file['path'], function (_err) {}); 
                                reject(err);
                                return false;
                            }


                            if(user.UserDatum.profileImage){
                               let _old_file = new User().getProfileImageLocation(user.UserDatum.profileImage);
                               fs.unlink(_old_file, function (_err) {}); 
                               fs.unlink(_old_file+"_98x98.jpg", function (_err) {}); 
                            }


                            user.UserDatum.profileImage = _file['filename'];
                            //console.log(user.UserDatum);
                            user.UserDatum.save({validate: false, fields: ['profileImage']}).then(user => {
                                resolve(_file['path']);
                            })
                            
                          }.bind(_file));

                    }

                }

            }catch (e) {
                reject(e);
            }
        });
    }

    User.prototype.updateUser = async (user, data) => {
        return new Promise((resolve, reject) => {
            console.log(data)

            Object.keys(data).forEach(key => {
                if (user._modelOptions.hasOwnProperty(key)) {
                    user._modelOptions[key] = data[key]
                }
            })
            user.setAttributes(data)
            user.validate().then(user => {
                user.save({validate: false}).then(user => {
                    user._modelOptions.oldPassword = null;
                    user.UserDatum.setAttributes(data)
                    user.UserDatum.save().then(datum => {
                        user.UserDatum = datum
                        resolve(user)
                    }).catch(err => {
                        // console.log(err)
                        reject(stringHelper.sequelizeValidationErrorsToArray(Object.assign({}, err).errors))
                    })
                }).catch(err => {
                    // console.log(err)
                    reject(err)
                })
            }).catch(err => {
                reject(stringHelper.sequelizeValidationErrorsToArray(Object.assign({}, err).errors))
            })

        })
    }

    User.prototype.login = async (data) => {
        return new Promise((resolve, reject) => {
            User.findOne({
                where: {
                    email: data.email,
                    password: data.password
                },
                include: [{
                    model: sequelize.models.Token
                }, {
                    model: sequelize.models.UserData
                }]
            }).then(user => {
                if (user == null) {
                    reject({error: 'Invalid credentials or user not found'})
                    return
                }
                resolve(user)
                return
            }).catch(err => {
                reject(err)
            })
        })
    }

    User.prototype.findUser = async (where) => {
        return new Promise((resolve, reject) => {
            User.findOne({
                where: where,
                include: [{
                    model: sequelize.models.Token
                }, {
                    model: sequelize.models.UserData
                }]
            }).then(user => {
                resolve(user)
                return
            }).catch(err => {
                reject(err)
            })
        })
    }

    User.prototype.checkEmail = async (email) => {
        return new Promise((resolve, reject) => {
            let test = new User()
            test.email = email
            // test.password = 5555555
            // test.passwordConfirm = 5555555
            test.validate({fields: ['email']}).then(() => {
                User.findOne({
                    where: {
                        email: email
                    }
                }).then(user => {
                    if (user != null) {
                        resolve(false)
                    } else {
                        resolve(true)
                    }
                }).catch(err => {
                    reject(err)
                })

            }).catch(e => {
                reject(stringHelper.sequelizeValidationErrorsToArray(Object.assign({}, e).errors))
            })
        })
    }

    User.prototype.resetPassword = async (code, newPassword) => {
        return new Promise((resolve, reject) => {

            if(!newPassword){
                reject('new password is empty')
            }

            //, { replacements: { UserId: user.id }}
            sequelize.query(
                "UPDATE `ResetPasswordCodes` SET `status` = 'expired' WHERE status = 'active' AND `createdAt` < NOW() - INTERVAL 1 HOUR"
            ).spread((results, metadata) => {
                // Results will be an empty array and metadata will contain the number of affected rows.
            })

            sequelize.query("SELECT * FROM `ResetPasswordCodes` WHERE status='active' AND code=:code", {replacements: { code: code}, type: sequelize.QueryTypes.SELECT})
            .then(async (_resetPasswordCode) => {
                if (_resetPasswordCode && _resetPasswordCode.length) {
                    _resetPasswordCode = _resetPasswordCode[0];
                    try {

                        User.findOne({where : {id : _resetPasswordCode.UserId}}).then(user => {
                            user.password = md5(newPassword);
                            user.save({validate: false, fields: ['password']}).then(__user => {

                                sequelize.query(
                                    "UPDATE `ResetPasswordCodes` SET `status` = 'used' WHERE code=:code", {replacements: {code}}
                                ).spread((results, metadata) => {
                                    resolve("ok")
                                })

                            }).catch(err => {
                                console.log(err)
                                reject(err)
                                return
                            })
                        }).catch(err => {
                            reject(err)
                        })
                        
                    }catch(err){
                        reject(err)
                    }

                } else {
                    reject("We couldn't find your request with "+code+" code")
                }
            }).catch(err => {
                reject(err)
            })
        })
    }


    User.prototype.forgotPassword = async (email) => {
        return new Promise((resolve, reject) => {

            User.findOne({
                where: {
                    email: email
                }
            }).then(async (user) => {
                if (user != null) {

                    try{

                        // Field 'UserId' doesn't have a default value
                        const code = uuid();
                        sequelize.query(
                            'INSERT INTO ResetPasswordCodes (status, code, UserId, createdAt, updatedAt) VALUES ("active", :code, :UserId, NOW(), NOW())',
                            { replacements: { UserId: user.id, code: code  }}
                        ).spread((results, metadata) => {
                            // Results will be an empty array and metadata will contain the number of affected rows.
                        })

                        resolve({status: 200, code})
                    }catch(err){
                        reject(err)
                    }

                } else {
                    reject("We couldn't find your account with "+email+" email")
                }
            }).catch(err => {
                reject(err)
            })

        })


    }

    User.prototype.renderOne = (user) => {
        console.log('user model', user);
        user = user.dataValues


        let userDataIgnoreKeys = ['id', 'UserId', 'createdAt', 'updatedAt']
        let userIgnoreKeys = ['password', 'admin', 'createdAt', 'updatedAt']


        let userData = {}
        if (user.UserDatum && Object.keys(user.UserDatum).length > 0) {
            userData = user.UserDatum.dataValues
        }
        if (user.UserDatum) delete user.UserDatum


        Object.keys(user).forEach(key => {
            if (userIgnoreKeys.indexOf(key) > -1) {
                delete user[key]
            }
        })

        
        Object.keys(userData).forEach(dkey => {
            if (userDataIgnoreKeys.indexOf(dkey) > -1) return
            user[dkey] = userData[dkey]
        })

        //console.log(profileImageUrl);
        user.profileImageUrl = new User().getProfileImageUrl(user.profileImage);
        //user.UserDatum.profileImage = "uploads/profile-images/7e9ba4664d83727cada2268819945182";

        return user
    }

    User.prototype.checkTwitter = async (data) => {
        return new Promise((resolve, reject) => {
            let parsedData = {
                twitterId: data.id,
                firstName: data.displayName,
                lastName: data.username,
            }

            new User().findUser({twitterId: parsedData.twitterId}).then(user => {
                if (user != null) {
                    resolve(user)
                    return
                } else {
                    let unsavedUser = new User()
                    unsavedUser.setAttributes(parsedData)
                    unsavedUser.social = 1
                    unsavedUser.validate({fields: ['twitterId', 'firstName', 'lastName']}).then(user => {
                        user.save({validate: false}).then(user => {
                            let uData = new sequelize.models.UserData()
                            uData.setAttributes(parsedData)
                            uData.UserId = user.id
                            uData.save({validate: false}).then(async uData => {
                                let token = await new sequelize.models.Token().addToken(user)
                                new User().findUser({id: user.id}).then(user => {
                                    resolve(user)
                                    return
                                }).catch(err => {
                                    console.log(err)
                                    reject(err)
                                    return
                                })
                            }).catch(err => {
                                console.log(err)
                                reject(err)
                                return
                            })
                        }).catch(err => {
                            console.log(err)
                            reject(err)
                            return
                        })
                    }).catch(err => {
                        console.log(err)
                        reject(err)
                        return
                    })
                }
            }).catch(err => {
                reject(err)
            })
        })
    }

    User.prototype.checkFacebook = async (data) => {
        return new Promise((resolve, reject) => {
            let userData = {}
            Object.keys(data).forEach(key => {
                if (key == 'name') return
                if (key == 'id') {
                    userData['facebookId'] = data[key]
                    delete data[key]
                }
                userData[key.replace(/(-|\_)([a-z])/g, function (g) {
                    return g[1].toUpperCase()
                })] = data[key]
            })
            new User().findUser({email: userData.email}).then(user => {
                if (user == null) {
                    let unsavedUser = new User()
                    unsavedUser.setAttributes(userData)
                    unsavedUser.social = 1
                    unsavedUser.validate({fields: ['email', 'firstName', 'lastName', 'facebookId']}).then(user => {
                        user.save({validate: false}).then(user => {
                            let uData = new sequelize.models.UserData()
                            uData.setAttributes(userData)
                            uData.UserId = user.id
                            uData.save({validate: false}).then(async uData => {
                                let token = await new sequelize.models.Token().addToken(user)
                                new User().findUser({id: user.id}).then(user => {
                                    resolve(user)
                                }).catch(err => {
                                    console.log(err)
                                    reject(err)
                                    return
                                })
                            }).catch(err => {
                                console.log(err)
                                reject(err)
                                return
                            })
                        }).catch(err => {
                            console.log(err)
                            reject(err)
                            return
                        })
                    }).catch(err => {
                        console.log(err)
                        reject(err)
                        return
                    })
                } else {
                    resolve(user)
                    return
                }
            }).catch(err => {
                reject(err)
            })
        })
    }

    User.prototype.checkGoogle = async (data) => {
        return new Promise((resolve, reject) => {
            let userData = {}
            Object.keys(data).forEach(key => {
                if (key == 'name') return
                if (key == 'id') {
                    userData['googleId'] = data[key]
                    delete data[key]
                }
                userData[key.replace(/(-|\_)([a-z])/g, function (g) {
                    return g[1].toUpperCase()
                })] = data[key]
            })
            new User().findUser({email: userData.email}).then(user => {
                if (user == null) {
                    let unsavedUser = new User()
                    unsavedUser.setAttributes(userData)
                    unsavedUser.social = 1
                    unsavedUser.validate({fields: ['email', 'firstName', 'lastName', 'googleId']}).then(user => {
                        user.save({validate: false}).then(user => {
                            let uData = new sequelize.models.UserData()
                            uData.setAttributes(userData)
                            uData.UserId = user.id
                            uData.save({validate: false}).then(async uData => {
                                let token = await new sequelize.models.Token().addToken(user)
                                new User().findUser({id: user.id}).then(user => {
                                    resolve(user)
                                }).catch(err => {
                                    console.log(err)
                                    reject(err)
                                    return
                                })
                            }).catch(err => {
                                console.log(err)
                                reject(err)
                                return
                            })
                        }).catch(err => {
                            console.log(err)
                            reject(err)
                            return
                        })
                    }).catch(err => {
                        console.log(err)
                        reject(err)
                        return
                    })
                } else {
                    resolve(user)
                    return
                }
            }).catch(err => {
                reject(err)
            })
        })
    }

    User.prototype.registerSimple = async (data) => {

        return new Promise((resolve, reject) => {
            let user = new User()
            user.setAttributes(data)
            user._modelOptions.passwordConfirm = data.passwordConfirm
            user._modelOptions.scenario = 'create'
            user.validate().then(unsavedUser => {
                let userData = new sequelize.models.UserData()
                userData.setAttributes(data)
                userData.validate().then(res => {
                    unsavedUser._modelOptions.scenario = null
                    unsavedUser.save().then(user => {
                        userData.UserId = user.id
                        userData.save().then(async userData => {
                            await new sequelize.models.Token().addToken(user)

                            new User().findUser({id: user.id}).then(user => {
                                resolve(new User().renderOne(user))
                                return
                            }).catch(err => {
                                reject(err)
                                return
                            })
                        }).catch(err => {
                            reject(err)
                            return
                        })
                    }).catch(err => {
                        console.log('========', err);
                        reject(err)
                        return
                    })
                }).catch(udErr => {
                    reject(stringHelper.sequelizeValidationErrorsToArray(Object.assign({}, udErr).errors))
                    return
                })

            }).catch(e => {
                reject(stringHelper.sequelizeValidationErrorsToArray(Object.assign({}, e).errors))
            })
        })

    }

    User.prototype.getAdminByCredentials = (data) => {
        return new Promise((resolve, reject) => {
            User.findOne({
                where: {
                    email: data.email.toLowerCase(),
                    password: md5(data.password),
                    admin: 1
                },
                include: [{
                    model: sequelize.models.Token
                }]
            }).then(async user => {
                if (user.Tokens.length == 0) {
                    let token = await new sequelize.models.Token().addToken(user)
                    user.Tokens.push(token);
                }
                resolve(user)
            }).catch(e => {
                reject(e)
                return
            })
        })
    }

    User.prototype.setSfToken = async (id, sf_token, sf_instance_url) => {
        return new Promise((resolve, reject) => {
            User.update(
                {
                    sf_token,
                    sf_instance_url,
                    sf_token_expired: moment().add(1, 'hour').format('YYYY-MM-DD hh:mm:ss')
                },
              {where: {id} },
            ).catch(err => {
                console.log(err);
                reject(e)
            })
            resolve('ok')
        });
    }

    User.prototype.getSFToken = async (id) => {
        return new Promise( async (resolve, reject) => {
            try{
                const user = await new User().findUser({ id });
                const now = moment().format('YYYY-MM-DD hh:mm:ss')
                if (user.sf_token_expired && moment(user.sf_token_expired).isAfter(now)) {
                    resolve({ access_token: user.sf_token, instance_url: user.sf_instance_url, status: 'ok' })
                } else {
                    const sfATRes = await authSalesforce();
                    let access_token = sfATRes.access_token;
                    let instance_url = sfATRes.instance_url;
                    if (!access_token) {
                        reject({message: 'Something wrong happend on Sales Force', status: 'failure'});
                    } else {
                        await new User().setSfToken(id, access_token, instance_url);
                        resolve({ access_token, instance_url, status: 'ok' })
                    }
                }
            } catch (e) {
                reject(e);
            }
        })
    }

    return User
}