'use strict';
module.exports = {
    up: (queryInterface, Sequelize) => {
        return queryInterface.createTable('UserData', {
            id: {
                allowNull: false,
                autoIncrement: true,
                primaryKey: true,
                type: Sequelize.INTEGER
            },
            UserId: {
                type: Sequelize.INTEGER,
                onDelete: "CASCADE",
                allowNull: false,
                references: {
                    model: 'Users',
                    key: 'id'
                }
            },
            firstName: {
                type: Sequelize.STRING
            },
            lastName: {
                type: Sequelize.STRING
            },
            zipCode: {
                type: Sequelize.INTEGER
            },
            age: {
                type: Sequelize.INTEGER
            },
            gender: {
                type: Sequelize.STRING
            },
            height: {
                type: Sequelize.STRING
            },
            weight: {
                type: Sequelize.STRING
            },
            lifeStyle: {
                type: Sequelize.STRING
            },
            jobType: {
                type: Sequelize.STRING
            },
            weeklyPhysicalActivity: {
                type: Sequelize.STRING
            },
            goals: {
                type: Sequelize.STRING
            },
            createdAt: {
                allowNull: false,
                type: Sequelize.DATE,
                defaultValue: Sequelize.NOW
            },
            updatedAt: {
                allowNull: false,
                type: Sequelize.DATE,
                defaultValue: Sequelize.NOW
            }
        });
    },
    down: (queryInterface, Sequelize) => {
        return queryInterface.dropTable('UserData');
    }
};