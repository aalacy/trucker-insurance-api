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
        type: Sequelize.BLOB
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
        type: Sequelize.BLOB
      },
      garagingAddress: {
        type: Sequelize.BLOB
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
        type: Sequelize.BLOB
      },
      currentEldProvider: {
        type: Sequelize.BLOB
      },
      cargoHauled: {
        type: Sequelize.BLOB
      },
      cargoGroup: {
        type: Sequelize.BLOB
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
        type: Sequelize.BLOB
      },
      ownerInformationList: {
        type: Sequelize.BLOB
      },
      vehicleInformationList: {
        type: Sequelize.BLOB
      },
      comments: {
        type: Sequelize.TEXT
      },
      attachmentList: {
        type: Sequelize.BLOB
      },
      signSignature: {
        type: Sequelize.BLOB
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