import { useEffect, useRef, useState } from "react";
import Tree from "react-d3-tree";
import "./DecisionTree.css";

// Player colors for visual distinction
const PLAYER_COLORS = {
  root: { bg: "#6366f1", border: "#4f46e5", text: "#fff" },
  0: { bg: "#3b82f6", border: "#2563eb", text: "#fff", name: "You" },
  1: { bg: "#f59e0b", border: "#d97706", text: "#fff", name: "Opp 1" },
  2: { bg: "#ef4444", border: "#dc2626", text: "#fff", name: "Opp 2" },
  3: { bg: "#8b5cf6", border: "#7c3aed", text: "#fff", name: "Opp 3" },
  leaf: { bg: "#10b981", border: "#059669", text: "#fff" },
  best: { bg: "#10b981", border: "#047857", text: "#fff" },
};

const DecisionTree = ({ treeData, bestMove }) => {
  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [tooltip, setTooltip] = useState({
    visible: false,
    x: 0,
    y: 0,
    content: null,
  });
  const treeContainerRef = useRef(null);

  useEffect(() => {
    if (treeContainerRef.current) {
      const rect = treeContainerRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width, height: rect.height });
      setTranslate({
        x: rect.width / 2,
        y: 80,
      });
    }
  }, [treeData]);

  // Handle tooltip
  const showTooltip = (event, nodeDatum) => {
    const rect = treeContainerRef.current.getBoundingClientRect();
    setTooltip({
      visible: true,
      x: event.clientX - rect.left + 10,
      y: event.clientY - rect.top - 10,
      content: nodeDatum,
    });
  };

  const hideTooltip = () => {
    setTooltip({ ...tooltip, visible: false });
  };

  // Transform the tree structure to react-d3-tree format
  const transformTreeData = (nodeId, nodesMap, depth = 0) => {
    const node = nodesMap[nodeId];
    if (!node) return null;

    const isLeaf = !node.children || node.children.length === 0;
    const isRoot = node.parent_id === null;
    const isBestMove = node.label === bestMove && node.player_index === 0;

    // Truncate long labels for display
    const truncateLabel = (label, maxLen = 20) => {
      if (!label) return "";
      return label.length > maxLen ? label.substring(0, maxLen) + "..." : label;
    };

    const transformed = {
      name: truncateLabel(node.label),
      fullName: node.label,
      attributes: {
        score: node.score,
        playerIndex: node.player_index,
        isLeaf,
        isRoot,
        isBestMove,
        depth,
      },
      children: [],
    };

    if (node.children && node.children.length > 0) {
      transformed.children = node.children
        .map((childId) => transformTreeData(childId, nodesMap, depth + 1))
        .filter((child) => child !== null);
    }

    return transformed;
  };

  if (!treeData || Object.keys(treeData).length === 0) {
    return (
      <div className="tree-container">
        <p className="no-data">No decision tree data available</p>
      </div>
    );
  }

  const nodesMap = treeData;
  const rootId =
    Object.keys(nodesMap).find((key) => nodesMap[key].parent_id === null) ||
    "node_0";
  const transformedData = transformTreeData(rootId, nodesMap);

  if (!transformedData) {
    return (
      <div className="tree-container">
        <p className="no-data">Unable to render tree structure</p>
      </div>
    );
  }

  // Get unique players for legend
  const players = new Set();
  Object.values(nodesMap).forEach((node) => {
    if (node.player_index !== null && node.player_index !== undefined) {
      players.add(node.player_index);
    }
  });

  // Custom node rendering
  const renderCustomNode = ({ nodeDatum, toggleNode }) => {
    const { isLeaf, isRoot, isBestMove, playerIndex, score } =
      nodeDatum.attributes || {};

    // Determine colors
    let colors;
    if (isBestMove) {
      colors = PLAYER_COLORS.best;
    } else if (isRoot) {
      colors = PLAYER_COLORS.root;
    } else if (isLeaf) {
      colors = PLAYER_COLORS.leaf;
    } else {
      colors = PLAYER_COLORS[playerIndex] || PLAYER_COLORS[0];
    }

    // Compact node sizes - no text needed
    const nodeSize = isLeaf ? 24 : 36;

    return (
      <g
        onClick={toggleNode}
        onMouseEnter={(e) => showTooltip(e, nodeDatum)}
        onMouseLeave={hideTooltip}
        style={{ cursor: "pointer" }}
      >
        {/* Glow effect for best move */}
        {isBestMove && (
          <circle
            r={nodeSize / 2 + 6}
            fill="#10b981"
            opacity={0.3}
            style={{ filter: "blur(6px)" }}
          />
        )}

        {/* Main node circle */}
        <circle
          r={nodeSize / 2}
          fill={colors.bg}
          stroke={colors.border}
          strokeWidth={isBestMove ? 3 : 2}
          style={{
            filter: `drop-shadow(0 2px 6px ${colors.bg}50)`,
            transition: "all 0.2s ease",
          }}
        />

        {/* Inner circle for visual depth - no text */}
        <circle
          r={nodeSize / 2 - 4}
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth={1}
        />

        {/* Best move star */}
        {isBestMove && (
          <text
            x={nodeSize / 2 + 8}
            y={-nodeSize / 2 + 4}
            fontSize="14"
            style={{ pointerEvents: "none" }}
          >
            ⭐
          </text>
        )}
      </g>
    );
  };

  // Custom path style
  const getDynamicPathClass = ({ source, target }) => {
    if (target?.data?.attributes?.isBestMove) {
      return "link-best";
    }
    return "link-normal";
  };

  return (
    <div className="tree-container" ref={treeContainerRef}>
      {/* Legend */}
      <div className="tree-legend">
        <div className="legend-title">Legend</div>

        {/* Best Move - highlighted at top */}
        <div className="legend-item best">
          <span
            className="legend-box"
            style={{
              background: PLAYER_COLORS.best.bg,
              boxShadow: "0 0 8px #10b981",
            }}
          ></span>
          <span>⭐ Best Move</span>
        </div>

        <div className="legend-divider"></div>

        {/* Player types */}
        <div className="legend-item">
          <span
            className="legend-box"
            style={{ background: PLAYER_COLORS.root.bg }}
          ></span>
          <span>Root</span>
        </div>
        <div className="legend-item">
          <span
            className="legend-box"
            style={{ background: PLAYER_COLORS[0].bg }}
          ></span>
          <span>Your Moves</span>
        </div>
        {[...players]
          .filter((p) => p > 0)
          .sort()
          .map((p) => (
            <div key={p} className="legend-item">
              <span
                className="legend-box"
                style={{ background: PLAYER_COLORS[p]?.bg || "#888" }}
              ></span>
              <span>Opponent {p}</span>
            </div>
          ))}
        <div className="legend-item">
          <span
            className="legend-box"
            style={{ background: PLAYER_COLORS.leaf.bg }}
          ></span>
          <span>Outcomes</span>
        </div>
      </div>

      {/* Instructions */}
      <div className="tree-instructions">
        <span>🖱️ Drag to pan • Scroll to zoom • Hover for details</span>
      </div>

      {/* Tooltip */}
      {tooltip.visible && tooltip.content && (
        <div
          className="tree-tooltip"
          style={{
            left: tooltip.x,
            top: tooltip.y,
          }}
        >
          <div className="tooltip-header">
            {/* Player type badge */}
            {tooltip.content.attributes?.isRoot && (
              <span className="tooltip-badge root">Root</span>
            )}
            {tooltip.content.attributes?.isLeaf && (
              <span className="tooltip-badge leaf">Outcome</span>
            )}
            {!tooltip.content.attributes?.isRoot &&
              !tooltip.content.attributes?.isLeaf &&
              tooltip.content.attributes?.playerIndex !== null && (
                <span
                  className="tooltip-badge"
                  style={{
                    background:
                      PLAYER_COLORS[tooltip.content.attributes.playerIndex]?.bg,
                  }}
                >
                  {tooltip.content.attributes.playerIndex === 0
                    ? "Your Move"
                    : `Opponent ${tooltip.content.attributes.playerIndex}`}
                </span>
              )}

            {/* Best Move badge - separate line */}
            {tooltip.content.attributes?.isBestMove && (
              <span className="tooltip-badge best">⭐ Best Move</span>
            )}
          </div>
          {/* Show appropriate label based on node type */}
          {tooltip.content.attributes?.isRoot ? (
            <div className="tooltip-label">
              <span style={{ opacity: 0.7, fontSize: "11px" }}>
                Time Period:
              </span>
              <br />
              {tooltip.content.fullName}
            </div>
          ) : (
            <div className="tooltip-label">{tooltip.content.fullName}</div>
          )}
          {tooltip.content.attributes?.score !== null &&
            tooltip.content.attributes?.score !== undefined && (
              <div className="tooltip-score">
                Score:{" "}
                <strong>{tooltip.content.attributes.score.toFixed(3)}</strong>
              </div>
            )}
        </div>
      )}

      <Tree
        data={transformedData}
        translate={translate}
        dimensions={dimensions}
        orientation="vertical"
        pathFunc="step"
        renderCustomNodeElement={renderCustomNode}
        pathClassFunc={getDynamicPathClass}
        separation={{ siblings: 1, nonSiblings: 1.2 }}
        nodeSize={{ x: 80, y: 80 }}
        zoom={0.85}
        scaleExtent={{ min: 0.3, max: 3 }}
        enableLegacyTransitions={true}
        transitionDuration={300}
        depthFactor={80}
        shouldCollapseNeighborNodes={false}
        initialDepth={10}
      />
    </div>
  );
};

export default DecisionTree;
