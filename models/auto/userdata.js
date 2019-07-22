'use strict';
module.exports = (sequelize, DataTypes) => {
    const UserData = sequelize.define('UserData', {
        UserId: DataTypes.INTEGER,
        firstName: {
            type: DataTypes.STRING,
            allowNull: false,
            validate: {
                len: {
                    args: [2, 50],
                    msg: 'Invalid First Name'
                }
            }
        },
        lastName: {
            type: DataTypes.STRING,
            allowNull: false,
            validate: {
                len: {
                    args: [2, 50],
                    msg: 'Invalid Last Name'
                }
            }
        },
        zipCode: {
            type: DataTypes.INTEGER,
            allowNull: true,
            validate: {
                isNumeric: {
                    msg: 'ZipCode should contain numbers only'
                },
                len: {
                    args: [2, 6],
                    msg: 'Invalid ZipCode length'
                }
            }
        },
        age: {
            type: DataTypes.INTEGER,
            allowNull: true,
            validate: {
                isNumeric: {
                    msg: 'Age should contain numbers only'
                },
                len: {
                    args: [1, 13],
                    msg: 'Invalid Age'
                }
            }
        },
        gender: {
            type: DataTypes.STRING,
            allowNull: true,
            validate: {
                len: {
                    args: [4, 6],
                    msg: 'Gender required'
                },
                isIn : {
                    args : [['male', 'female']],
                    msg : 'Invalid gender'
                }
            }
        },
        height: {
            type: DataTypes.STRING,
            allowNull: true,
            validate : {
                len: {
                    args: [1, 255],
                    msg: 'Invalid Height'
                }
            }
        },
        weight: {
            type: DataTypes.STRING,
            allowNull: true,
            validate : {
                len: {
                    args: [1, 255],
                    msg: 'Invalid Weight'
                }
            }
        },
        lifeStyle: {
            type: DataTypes.STRING,
            allowNull: true,
            validate : {
                len: {
                    args: [1, 255],
                    msg: 'Invalid Lifestyle'
                }
            }
        },
        profileImage: {
            type: DataTypes.STRING,
            allowNull: true,
            validate : {}
        },
        jobType: {
            type: DataTypes.STRING,
            allowNull: true,
            validate : {
                len: {
                    args: [1, 255],
                    msg: 'Invalid Job Type'
                }
            }
        },
        weeklyPhysicalActivity: {
            type: DataTypes.STRING,
            allowNull: true,
            validate : {
                len: {
                    args: [1, 255],
                    msg: 'Invalid Weekly Physical Activity'
                }
            }
        },
        goals: {
            type: DataTypes.STRING,
            allowNull: true,
            validate : {
                len: {
                    args: [1, 255],
                    msg: 'Invalid Goals'
                }
            }
        }
    }, {
        validate: {}
    });
    UserData.associate = function (models) {
        // associations can be defined here
    };
    return UserData;
};