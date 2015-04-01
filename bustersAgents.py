# bustersAgents.py
# ----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import time
import random

class BustersAgent:
  "An agent that tracks and displays its beliefs about ghost positions."
  
  def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None ):
    inferenceType = util.lookup(inference, globals())
    self.inferenceModules = [inferenceType(a) for a in ghostAgents]
    
  def registerInitialState(self, gameState):
    "Initializes beliefs and inference modules"
    import __main__
    self.display = __main__._display
    for inference in self.inferenceModules: inference.initialize(gameState)
    self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
    self.firstMove = True
    
  def observationFunction(self, gameState):
    "Removes the ghost states from the gameState"
    agents = gameState.data.agentStates
    gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
    return gameState

  def getAction(self, gameState):
    "Updates beliefs, then chooses an action based on updated beliefs."
    for index, inf in enumerate(self.inferenceModules):
      if not self.firstMove: inf.elapseTime(gameState)
      self.firstMove = False
      inf.observeState(gameState)
      self.ghostBeliefs[index] = inf.getBeliefDistribution()
    self.display.updateDistributions(self.ghostBeliefs)
    return self.chooseAction(gameState)

  def chooseAction(self, gameState):
    "By default, a BustersAgent just stops.  This should be overridden."
    return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
  "An agent controlled by the keyboard that displays beliefs about ghost positions."
  
  def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None):
    KeyboardAgent.__init__(self, index)
    BustersAgent.__init__(self, index, inference, ghostAgents)
    
  def getAction(self, gameState):
    return BustersAgent.getAction(self, gameState)
    
  def chooseAction(self, gameState):
    return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions

class GreedyBustersAgent(BustersAgent):
  "An agent that charges the closest ghost."
  
  def registerInitialState(self, gameState):
    "Pre-computes the distance between every two points."
    BustersAgent.registerInitialState(self, gameState)
    self.distancer = Distancer(gameState.data.layout, False)
    
  def chooseAction(self, gameState):
    """
    First computes the most likely position of each ghost that 
    has not yet been captured, then chooses an action that brings 
    Pacman closer to the closest ghost (in maze distance!).
    
    To find the maze distance between any two positions, use:
    self.distancer.getDistance(pos1, pos2)
    
    To find the successor position of a position after an action:
    successorPosition = Actions.getSuccessor(position, action)
    
    livingGhostPositionDistributions, defined below, is a list of
    util.Counter objects equal to the position belief distributions
    for each of the ghosts that are still alive.  It is defined based
    on (these are implementation details about which you need not be
    concerned):

      1) gameState.getLivingGhosts(), a list of booleans, one for each
         agent, indicating whether or not the agent is alive.  Note
         that pacman is always agent 0, so the ghosts are agents 1,
         onwards (just as before).

      2) self.ghostBeliefs, the list of belief distributions for each
         of the ghosts (including ghosts that are not alive).  The
         indices into this list should be 1 less than indices into the
         gameState.getLivingGhosts() list.
     
    """
    pacmanPosition = gameState.getPacmanPosition()
    legal = [a for a in gameState.getLegalPacmanActions()]
    livingGhosts = gameState.getLivingGhosts()
    print "living ghosts:", livingGhosts
    livingGhostPositionDistributions = [beliefs for i,beliefs
                                        in enumerate(self.ghostBeliefs)
                                        if livingGhosts[i+1]]
    "*** YOUR CODE HERE ***"

    #need to find most likely location of each living ghost
    #pick the closest out of these likely locations
    #pick direction that goes towards that.
    totalClosestDist = 10000
    totalClosestPos = []
    for i,belief in enumerate(self.ghostBeliefs):
      ghostIndex = i+1
      if livingGhosts[ghostIndex]:
        print "Ghost " + str(ghostIndex) + " is alive."
        maxProb = 0
        maxPositions = []
        for b in belief.items():
          pos = b[0]
          prob = b[1]
          if prob >= maxProb:
            maxProb = prob
            maxPositions.append(pos)
        print maxProb
        print maxPositions
        print "Pacman is at location ", pacmanPosition
        closestDist = 10000
        closestPos = []
        for ghostPos in maxPositions:
          d = self.distancer.getDistance(pacmanPosition, ghostPos)
          if d < closestDist:
            closestDist = d
            closestPos = [ghostPos]
          elif d == closestDist:
            print ghostPos
            print closestPos
            closestPos.append(ghostPos)
        print "closestDist:", closestDist
        print "closestPos:", closestPos
        print "total", totalClosestDist, totalClosestPos
        if closestDist < totalClosestDist:
          print str(closestDist)+" is closer than "+str(totalClosestDist)
          totalClosestDist = closestDist
          totalClosestPos = []
          totalClosestPos.append(closestPos)
        #time.sleep(5)
      else:
        print "Ghost " + str(ghostIndex) + " is dead."

    #We've now found the closest most likely position of a ghost.
    print "Total closest dist:", totalClosestDist
    print "Total closest pos:", totalClosestPos

    if len(totalClosestPos) == 1:
      print "Only one closestPos"
      totalClosestPos = totalClosestPos[0]
    print totalClosestPos
    #Now need to figure out which direction to move there.
    minD = 100000
    minDirection = []
    for action in legal:
      print "Location before move is", pacmanPosition
      print "Moving ", action
      successorPosition = Actions.getSuccessor(pacmanPosition, action)
      print "Now at location", successorPosition
      print totalClosestPos
      d = self.distancer.getDistance(successorPosition, totalClosestPos)
      print "d", d
      if d < minD:
        minD = d
        minDirection = []
        minDirection.append(action)
      elif d == minD:
        minDirection.append(action)
    numDirections = len(minDirection)
    bestDir = minDirection[random.randint(0, numDirections-1)]
    print bestDir

    return bestDir