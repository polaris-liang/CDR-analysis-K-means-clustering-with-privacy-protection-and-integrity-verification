/*TMC smart contract 
//the contract should be signed by the TC and the CS.
//treat the TC and CS as two rational players.
*/
pragma solidity ^0.4.4;

contract players {
    
    //addresses of parties
    address public TC;
    address public CS;

    mapping (address => uint ) public results;
    mapping (address => bool ) public hasBid;
    mapping (address => bool ) public hasDeliver;
    

    //deadlines
    uint public T1 = now + 10 minutes;
    uint public T2 = T1 + 10 minutes;
    uint public T3 = T2 + 15 minutes;
    

    //amount of wage: piad by TC and paid to CS
    uint public w = 2 ;
    
    //amount deposit: paid by CS
    uint public d = 4 ;

   //all the states
    enum State {INIT, Created, Compute, Pay, Done, Error, Aborted, SendError}
    
    //current state
    State public state = State.INIT;

    //constructor
    function players() {
        CS = msg.sender;//
        TC = msg.sender;
    }


    //fallback function
    function() payable {
      throw;
    }
    
    //First Function Create
    //The TC needs to nominate workers before T1
    function Create (uint _w, uint _d, uint _T1, uint _T2, uint _T3) payable returns(bool){
          assert(msg.sender == TC);

          //initiate contract parameters
          w = _w ; d = _d;
          //CS = addr;

          //time 
    	  T1 = _T1;
          T2 = _T2;
          T3 = _T3;
          
          //current time
          uint T = now;
          
          //sanity checks
          assert(state == State.INIT );
          assert(T<T1 && T1<T2 && T2<T3);
          //must pay this amount into the contract
          assert(msg.value==(w));

          //change the state
          state = State.Created;
          
          //for debugging
          return true;
    }

    //Second Function BID();
    //The CS needs to pay the deposit before T1
    function Bid() payable returns (bool sta){
        //current time
        uint T = now; 
        
        //sanity checks
        assert(state == State.Created);
        assert(T < T1);
        assert(msg.value == d);
        assert(!hasBid[msg.sender]);
        assert(msg.sender == CS);

        hasBid[msg.sender] = true;
        
        //change state if both have bid
        if (hasBid[CS]== true){ 
            state = State.Compute;
            
        }

        //for debugging
        return true;
    }// end BID

    //Third Function DELIVER;
    //The CS needs to deliver the computation results before T2
    function Deliver () returns (bool D){
        //current time
        //uint T = now; 
        
        //sanity checks
        //assert(msg.sender == CS);
        //assert(state == State.Compute);
        //assert(T < T2);
        //assert(!hasDeliver[msg.sender]);
        
        //check the result returned or not
        //if (msg.sender == CS){
        //    hasDeliver[msg.sender] = true;
        //}
        

        // if CS delivered results then change the state;
        //if (hasDeliver[CS] == true) {
        //        state = State.Pay;
        //}
        
        //for debugging
        return true;
    } // end DELIVER

    //Fourth Function PAY;
    //TC verifies the integrity of the returned result
    function Pay (bool verify) payable returns (bool Do){
        //current time
        uint T = now;

        //sanity checks
        assert(state == State.Pay);
        assert(T < T3);
        
        
        bool succ;
        
        //if not delivered
        if (hasDeliver[CS] == false){
           //if CS did not sign the contrace, refund the wage to TC
           succ = TC.send(w);
           assert(succ);
           //change the state
           state = State.Done;
        }
        //if delivered
        else if (hasDeliver[CS] == true){
            //verify succeed
            if(verify==true){
                //pay CS and refund deposit
                succ = CS.send(w+d);
                assert(succ);
                
                //change the state
                state = State.Done;
                Do  = true;
            }
            //verify failed
            else if(verify==false){
                succ= TC.send(w);
                assert(succ);
                
                //change the state
                state = State.Done;
                Do  = true;
            }
            //shouldn't reach here
            else {
                Do = false;
                state = State.Error;
            }

        }
        //shouldn't reach here
        else {
            Do = false;
            state = State.Error;
        }
        
        //for debugging
        return Do;
    }// end of PAY

    //Fifth Function TIMER
    function Timer() returns (bool Time){
        uint T = now;
        bool succ;
        
        if ((T>=T1) && state == State.Created){
           //refund the TC
           succ= TC.send(w);
           assert(succ);
           
           //refund other party who has paid
           if (hasBid[CS]==true){
               succ= CS.send(d);
               assert(succ);
               
           }
           state = State.Aborted;
            
        }else if ((T>=T2) && state == State.Compute){
            //move to pay state
            state = State.Pay;
        }else if ((T>=T3) && state == State.Pay){
            //pay who has delivered a result
            if(hasDeliver[CS] == true){
               succ= CS.send(w+d);
               assert(succ);
            }

            //rest goes to the TC
           succ= TC.send(this.balance);
           assert(succ);
           state = State.Done;
           
        }

    }

    function reset() returns (bool){
      assert(msg.sender == TC);
      assert(state == State.Done||state==State.Aborted);
      
      delete results[CS];
      
      delete hasBid[CS];
      delete hasDeliver[CS];

      CS=0;
      
      w = 0; d = 0; T1 =0; T2 = 0; T3 = 0;

      state = State.INIT;

      if (!TC.send(address(this).balance)){return false;}
    }

    //return the state of this contract to be used by the others
    function getState() returns(uint x){
       x = uint(state);
    }

} // end prisoners contract