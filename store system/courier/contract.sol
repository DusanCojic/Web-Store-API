pragma solidity ^0.8.0;

contract OrderContract {

    address public owner; // account of a store owner
    address public customer; // account of a customer paying the order
    address public courier; // account of a courier assigned for the delivery

    uint public price; // price of the order in wei
    bool public paid; // indicates whether customer has paid
    bool public courierBound; // indicates whether courier has been bound
    bool public delivered; // indicates whether delivery is confirmed

    constructor (address _owner, address _customer, uint _price) {
        owner = _owner;
        customer = _customer;
        price = _price;
        paid = false;
        courierBound = false;
        delivered = false;
    }

    // core functions

    function bindCourier(address _courier) public {
        require(!courierBound, "Courier already assigned");
        courier = _courier;
        courierBound = true;
    }

    function pay() public payable {
        require(!paid, "Already paid");
        require(msg.value == price, "Incorrect payment amount");
        paid = true;
    }

    function confirmDelivery() public payable {
        require(paid, "Order not paid yet");
        require(courierBound, "Courier not assigned");
        require(!delivered, "Already delivered");

        delivered = true;

        uint ownerAmount = (price * 80) / 100;
        uint courierAmount = price - ownerAmount;

        payable(owner).transfer(ownerAmount);
        payable(courier).transfer(courierAmount);
    }

    // helper functions

    function getOrderState()
        public view
        returns (address _owner, address _customer, address _courier, uint _price, bool _paid, bool _delivered, bool _courierBound) {
            return (owner, customer, courier, price, paid, delivered, courierBound);
        }
}