'use strict';
module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.createTable('Companies', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      uuid: {
        type: Sequelize.STRING
      },
      businessStructureRaw: {
        type: Sequelize.JSON
      },
      name: {
        type: Sequelize.STRING
      },
      dotNumber: {
        type: Sequelize.STRING
      },
      dba: {
        type: Sequelize.STRING
      },
      phoneNumber: {
        type: Sequelize.STRING
      },
      mailingAddress: {
        type: Sequelize.JSON
      },
      garagingAddress: {
        type: Sequelize.JSON
      },
      emailAddress: {
        type: Sequelize.STRING
      },
      powerUnits: {
        type: Sequelize.STRING
      },
      mcNumber: {
        type: Sequelize.STRING
      },
      travelRadius: {
        type: Sequelize.STRING
      },
      currentCarrier: {
        type: Sequelize.STRING
      },
      currentEldProvider: {
        type: Sequelize.JSON
      },
      cargoHauled: {
        type: Sequelize.JSON
      },
      cargoGroup: {
        type: Sequelize.JSON
      },
      ownerName: {
        type: Sequelize.STRING
      },
      businessStructure: {
        type: Sequelize.STRING
      },
      businessType: {
        type: Sequelize.STRING
      },
      driverInformationList: {
        type: Sequelize.JSON
      },
      ownerInformationList: {
        type: Sequelize.JSON
      },
      vehicleInformationList: {
        type: Sequelize.JSON
      },
      comments: {
        type: Sequelize.TEXT
      },
      attachmentList: {
        type: Sequelize.JSON
      },
      signSignature: {
        type: Sequelize.JSON
      },
      createdAt: {
        allowNull: false,
        type: Sequelize.DATE
      },
      updatedAt: {
        allowNull: false,
        type: Sequelize.DATE
      }
    });
  },
  down: (queryInterface, Sequelize) => {
    return queryInterface.dropTable('Companies');
  }
};